#!/usr/bin/env python3

"""
Multiple Test Execution for Statistical Analysis
Runs N tests to collect statistical data for comprehensive reporting
"""

import os
import sys
import json
import time
from datetime import datetime
from web3 import Web3
from dotenv import load_dotenv
import statistics

# Configuration
CHAIN_1_RPC = "https://ethereum-sepolia-rpc.publicnode.com"
CHAIN_2_RPC = "https://sepolia.base.org"
CHAIN_1_NAME = "Sepolia"
CHAIN_2_NAME = "Base Sepolia"
CHAIN_1_EXPLORER = "https://sepolia.etherscan.io"
CHAIN_2_EXPLORER = "https://sepolia.basescan.org"

from config import CONTRACT_CHAIN_1, CONTRACT_CHAIN_2, CONTRACT_ARTIFACTS_PATH

class MultiTestRunner:
    def __init__(self, num_tests=100):
        self.num_tests = num_tests
        self.results = {
            "test_metadata": {
                "test_date": datetime.now().isoformat(),
                "num_tests": num_tests,
                "test_type": "statistical_sampling",
                "trl_level": 8
            },
            "individual_tests": [],
            "statistical_analysis": {},
            "aggregated_metrics": {}
        }
        
        # Load environment
        env_path = os.path.join(os.path.dirname(__file__), "../../../../EVM/.env")
        load_dotenv(env_path)
        
        # Connect to chains
        self.w3_source = Web3(Web3.HTTPProvider(CHAIN_1_RPC))
        self.w3_dest = Web3(Web3.HTTPProvider(CHAIN_2_RPC))
        
        # Load contract
        with open(os.path.join(os.path.dirname(__file__), CONTRACT_ARTIFACTS_PATH), 'r') as f:
            contract_data = json.load(f)
        self.abi = contract_data["abi"]
        
        self.contract_source = self.w3_source.eth.contract(address=CONTRACT_CHAIN_1, abi=self.abi)
        self.contract_dest = self.w3_dest.eth.contract(address=CONTRACT_CHAIN_2, abi=self.abi)
        
        # Get private keys
        self.private_key_source = os.getenv("PRIVATE_KEY_SEPOLIA")
        self.private_key_dest = os.getenv("PRIVATE_KEY_BASE")
        
        if not self.private_key_source.startswith('0x'):
            self.private_key_source = '0x' + self.private_key_source
        if not self.private_key_dest.startswith('0x'):
            self.private_key_dest = '0x' + self.private_key_dest
        
        self.account_source = self.w3_source.eth.account.from_key(self.private_key_source)
        self.account_dest = self.w3_dest.eth.account.from_key(self.private_key_dest)
    
    def run_single_test(self, test_number):
        """Run a single complete test cycle"""
        
        print(f"\n{'='*70}")
        print(f"Test {test_number}/{self.num_tests}")
        print(f"{'='*70}")
        
        test_result = {
            "test_number": test_number,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "metrics": {}
        }
        
        try:
            # Step 1: Create Battle
            print(f"Creating battle on {CHAIN_1_NAME}...")
            creation_start = time.time()
            
            bet_amount = self.w3_source.to_wei(0.0001, 'ether')  # Reduced from 0.01 to 0.0001 ETH
            battle_type = "Football Freestyle"
            
            nonce_source = self.w3_source.eth.get_transaction_count(self.account_source.address)
            gas_price_source = self.w3_source.eth.gas_price
            
            tx = self.contract_source.functions.createBattle(battle_type).build_transaction({
                'from': self.account_source.address,
                'value': bet_amount,
                'gas': 500000,
                'gasPrice': gas_price_source,
                'nonce': nonce_source,
            })
            
            signed_tx = self.w3_source.eth.account.sign_transaction(tx, self.private_key_source)
            tx_hash_creation = self.w3_source.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            receipt_creation = self.w3_source.eth.wait_for_transaction_receipt(tx_hash_creation, timeout=120)
            creation_time = time.time() - creation_start
            
            if receipt_creation.status != 1:
                test_result["status"] = "failed_creation"
                return test_result
            
            # Extract battle ID
            battle_id = None
            for log in receipt_creation.logs:
                try:
                    decoded_log = self.contract_source.events.BattleCreated().process_log(log)
                    battle_id = decoded_log['args']['battleId']
                    break
                except:
                    continue
            
            if not battle_id:
                test_result["status"] = "failed_no_battle_id"
                return test_result
            
            test_result["battle_id"] = battle_id.hex()
            test_result["creation_tx"] = tx_hash_creation.hex()
            
            print(f"  ✅ Battle created: {battle_id.hex()[:16]}...")
            print(f"  Time: {creation_time:.2f}s, Gas: {receipt_creation.gasUsed:,}")
            print(f"  Sepolia TX: https://sepolia.etherscan.io/tx/{tx_hash_creation.hex()}")
            
            # Step 2: Replicate Battle
            print(f"Replicating to {CHAIN_2_NAME}...")
            
            try:
                # Fetch battle data
                fetch_start = time.time()
                battle = self.contract_source.functions.getBattle(battle_id).call()
                fetch_time = time.time() - fetch_start
                
                # Replicate
                replication_start = time.time()
                
                nonce_dest = self.w3_dest.eth.get_transaction_count(self.account_dest.address)
                gas_price_dest = self.w3_dest.eth.gas_price
                
                tx_repl = self.contract_dest.functions.replicateBattle(
                    battle[0], battle[1], battle[3], battle[8]
                ).build_transaction({
                    'from': self.account_dest.address,
                    'gas': 500000,
                    'gasPrice': gas_price_dest,
                    'nonce': nonce_dest,
                })
                
                signed_tx_repl = self.w3_dest.eth.account.sign_transaction(tx_repl, self.private_key_dest)
                tx_hash_replication = self.w3_dest.eth.send_raw_transaction(signed_tx_repl.raw_transaction)
                
                receipt_replication = self.w3_dest.eth.wait_for_transaction_receipt(tx_hash_replication, timeout=120)
                replication_time = time.time() - replication_start
                
                if receipt_replication.status != 1:
                    print(f"  ❌ Replication transaction failed (status=0)")
                    print(f"  Base TX: https://sepolia.basescan.org/tx/{tx_hash_replication.hex()}")
                    test_result["status"] = "failed_replication"
                    test_result["error"] = "Transaction reverted"
                    test_result["replication_tx"] = tx_hash_replication.hex()
                    return test_result
                    
            except Exception as repl_error:
                print(f"  ❌ Replication error: {repl_error}")
                test_result["status"] = "failed_replication"
                test_result["error"] = str(repl_error)
                return test_result
            
            test_result["replication_tx"] = tx_hash_replication.hex()
            
            print(f"  ✅ Replicated")
            print(f"  Sync time: {replication_time:.2f}s, Gas: {receipt_replication.gasUsed:,}")
            print(f"  Base TX: https://sepolia.basescan.org/tx/{tx_hash_replication.hex()}")
            
            # Step 3: Verify Consistency
            time.sleep(3)  # Let chain settle (increased for public testnets)
            
            battle_dest = self.contract_dest.functions.getBattle(battle_id).call()
            
            consistency = (
                battle[0] == battle_dest[0] and
                battle[1] == battle_dest[1] and
                battle[3] == battle_dest[3] and
                battle[8] == battle_dest[8]
            )
            
            # Store metrics
            test_result["metrics"] = {
                "creation_time_seconds": creation_time,
                "creation_gas_used": receipt_creation.gasUsed,
                "creation_gas_price_gwei": float(self.w3_source.from_wei(gas_price_source, 'gwei')),
                "creation_cost_eth": float(self.w3_source.from_wei(receipt_creation.gasUsed * gas_price_source, 'ether')),
                "fetch_time_seconds": fetch_time,
                "replication_time_seconds": replication_time,
                "replication_gas_used": receipt_replication.gasUsed,
                "replication_gas_price_gwei": float(self.w3_dest.from_wei(gas_price_dest, 'gwei')),
                "replication_cost_eth": float(self.w3_dest.from_wei(receipt_replication.gasUsed * gas_price_dest, 'ether')),
                "total_sync_time_seconds": fetch_time + replication_time,
                "end_to_end_time_seconds": creation_time + fetch_time + replication_time,
                "data_consistency": consistency,
                "total_gas_used": receipt_creation.gasUsed + receipt_replication.gasUsed,
                "total_cost_eth": float(self.w3_source.from_wei(receipt_creation.gasUsed * gas_price_source, 'ether')) + 
                                 float(self.w3_dest.from_wei(receipt_replication.gasUsed * gas_price_dest, 'ether'))
            }
            
            test_result["status"] = "success" if consistency else "inconsistent"
            
            print(f"  ✅ Consistency: {'✅ PASS' if consistency else '❌ FAIL'}")
            
            return test_result
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            test_result["status"] = "error"
            test_result["error"] = str(e)
            return test_result
    
    def calculate_statistics(self):
        """Calculate statistical metrics from all tests"""
        
        successful_tests = [t for t in self.results["individual_tests"] if t["status"] == "success"]
        
        if not successful_tests:
            print("❌ No successful tests to analyze")
            return
        
        print(f"\n{'='*70}")
        print(f"Calculating statistics from {len(successful_tests)} successful tests...")
        print(f"{'='*70}")
        
        # Extract metrics
        metrics_to_analyze = [
            "creation_time_seconds",
            "creation_gas_used",
            "replication_time_seconds",
            "replication_gas_used",
            "total_sync_time_seconds",
            "end_to_end_time_seconds",
            "total_gas_used",
            "total_cost_eth"
        ]
        
        stats = {}
        
        for metric in metrics_to_analyze:
            values = [t["metrics"][metric] for t in successful_tests if metric in t["metrics"]]
            
            if values:
                stats[metric] = {
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values),
                    "sample_size": len(values)
                }
        
        self.results["statistical_analysis"] = stats
        
        # Calculate success rate
        total_tests = len(self.results["individual_tests"])
        successful = len(successful_tests)
        consistency_rate = len([t for t in successful_tests if t["metrics"].get("data_consistency", False)])
        
        self.results["aggregated_metrics"] = {
            "total_tests_run": total_tests,
            "successful_tests": successful,
            "failed_tests": total_tests - successful,
            "success_rate_percentage": (successful / total_tests * 100) if total_tests > 0 else 0,
            "data_consistency_rate_percentage": (consistency_rate / successful * 100) if successful > 0 else 0,
            "avg_sync_time_seconds": stats["total_sync_time_seconds"]["mean"] if "total_sync_time_seconds" in stats else 0,
            "avg_cost_usd": stats["total_cost_eth"]["mean"] * 2600 if "total_cost_eth" in stats else 0  # ~$2600 ETH
        }
        
        # Print summary
        print(f"\n📊 Statistical Summary:")
        print(f"  Tests: {successful}/{total_tests} successful ({self.results['aggregated_metrics']['success_rate_percentage']:.1f}%)")
        print(f"  Sync Time: {stats['total_sync_time_seconds']['mean']:.2f}s ± {stats['total_sync_time_seconds']['std_dev']:.2f}s")
        print(f"  Range: {stats['total_sync_time_seconds']['min']:.2f}s - {stats['total_sync_time_seconds']['max']:.2f}s")
        print(f"  Cost: ${self.results['aggregated_metrics']['avg_cost_usd']:.4f} ± ${stats['total_cost_eth']['std_dev'] * 2600:.4f}")
        print(f"  Consistency: {consistency_rate}/{successful} ({self.results['aggregated_metrics']['data_consistency_rate_percentage']:.1f}%)")
    
    def save_results(self):
        """Save comprehensive results"""
        
        filename = f"multiple_tests_results_{self.num_tests}tests_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(os.path.dirname(__file__), "test_results", filename)
        
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📁 Results saved to: test_results/{filename}")
        
        return filepath
    
    def run_all_tests(self):
        """Execute all tests"""
        
        print(f"\n{'='*70}")
        print(f"  RUNNING {self.num_tests} TESTS FOR STATISTICAL ANALYSIS")
        print(f"{'='*70}")
        print(f"Source: {CHAIN_1_NAME} ({CONTRACT_CHAIN_1})")
        print(f"Destination: {CHAIN_2_NAME} ({CONTRACT_CHAIN_2})")
        
        start_time = time.time()
        
        for i in range(1, self.num_tests + 1):
            result = self.run_single_test(i)
            self.results["individual_tests"].append(result)
            
            # Small delay between tests to avoid rate limiting
            if i < self.num_tests:
                time.sleep(2)
        
        total_time = time.time() - start_time
        
        print(f"\n{'='*70}")
        print(f"All tests completed in {total_time/60:.1f} minutes")
        print(f"{'='*70}")
        
        self.calculate_statistics()
        filepath = self.save_results()
        
        return filepath

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Run multiple tests for statistical analysis')
    parser.add_argument('--num-tests', type=int, default=10, help='Number of tests to run (default: 10)')
    parser.add_argument('--yes', '-y', action='store_true', help='Skip confirmation prompt')
    args = parser.parse_args()
    
    runner = MultiTestRunner(num_tests=args.num_tests)
    
    # Confirm before running many tests
    if args.num_tests > 20 and not args.yes:
        print(f"\n⚠️  Warning: You're about to run {args.num_tests} tests.")
        print(f"This will:")
        print(f"  - Take approximately {args.num_tests * 0.15:.0f} minutes")
        print(f"  - Cost approximately ${args.num_tests * 0.0015:.2f} in testnet gas")
        print(f"  - Create {args.num_tests} battles on-chain")
        
        response = input(f"\nContinue? (yes/no): ").lower()
        if response != 'yes':
            print("Cancelled.")
            return 1
    
    filepath = runner.run_all_tests()
    
    print(f"\n{'='*70}")
    print(f"  STATISTICAL TESTING COMPLETE")
    print(f"{'='*70}")
    
    # Get successful tests count safely
    successful_tests = runner.results.get('aggregated_metrics', {}).get('successful_tests', 0)
    total_tests = runner.results.get('test_metadata', {}).get('num_tests', 0)
    
    print(f"\n✅ {successful_tests}/{total_tests} tests successful")
    print(f"✅ Results saved: {os.path.basename(filepath)}")
    print(f"\nUse this data for comprehensive reporting and statistical validation.")
    print(f"{'='*70}")
    
    # Automatically generate test results table
    print(f"\n🎯 GENERATING TEST RESULTS TABLE...")
    print(f"{'='*70}")
    try:
        import subprocess
        result = subprocess.run(['python3', 'test-results-analyzer.py'], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"⚠️ Could not generate table: {result.stderr}")
    except Exception as e:
        print(f"⚠️ Could not generate table: {e}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

