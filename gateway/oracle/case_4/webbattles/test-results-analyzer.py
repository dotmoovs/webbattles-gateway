#!/usr/bin/env python3
"""
Test Results Analyzer - Automatically generates formatted tables from test results
"""

import json
import os
from datetime import datetime
from web3 import Web3

def analyze_latest_tests():
    """Analyze the most recent test results and generate formatted table"""
    
    # Find the most recent test results file
    test_files = [f for f in os.listdir('test_results/') if f.endswith('.json') and 'multiple_tests_results' in f]
    if not test_files:
        print('❌ No test result files found')
        return
    
    # Get the most recent file
    latest_file = max(test_files, key=lambda x: os.path.getctime(f'test_results/{x}'))
    print(f'📁 Analyzing: {latest_file}')
    
    # Load the results
    with open(f'test_results/{latest_file}', 'r') as f:
        results = json.load(f)
    
    print('=' * 140)
    print('🎯 WEBBATTLES CROSS-CHAIN TEST RESULTS')
    print('=' * 140)
    print(f'📅 Test Date: {results["test_metadata"]["test_date"]}')
    print(f'📊 Number of Tests: {results["test_metadata"]["num_tests"]}')
    print(f'🎯 TRL Level: {results["test_metadata"]["trl_level"]}')
    print('=' * 140)
    
    print('\n📋 COMPLETE TEST RESULTS TABLE')
    print('=' * 140)
    print(f'{"Test#":<6} {"Battle ID":<20} {"Sepolia TX":<20} {"Base TX":<20} {"Create Time":<12} {"Sync Time":<12} {"Consistency":<12} {"Gas Used":<10} {"Cost (ETH)":<12} {"Status":<15}')
    print('-' * 140)
    
    successful_tests = 0
    failed_tests = 0
    error_tests = 0
    total_gas = 0
    total_cost = 0
    total_sync_time = 0
    
    for test in results['individual_tests']:
        test_num = test.get('test_number', 'N/A')
        battle_id = test.get('battle_id', 'N/A')
        sepolia_tx = test.get('creation_tx', 'N/A')
        base_tx = test.get('replication_tx', 'N/A')
        status = test.get('status', 'N/A')
        timestamp = test.get('timestamp', 'N/A')
        
        # Initialize metrics
        create_time = 'N/A'
        sync_time = 'N/A'
        consistency = 'N/A'
        gas_used = 'N/A'
        cost_eth = 'N/A'
        
        # Get metrics if available
        metrics = test.get('metrics', {})
        if metrics:
            # Use the correct field names from the JSON
            create_time = f"{metrics.get('creation_time_seconds', 0):.2f}s"
            sync_time = f"{metrics.get('total_sync_time_seconds', 0):.2f}s"
            gas_used = metrics.get('total_gas_used', 0)
            cost_eth = f"{metrics.get('total_cost_eth', 0):.8f}"
            
            if gas_used != 'N/A' and gas_used != 0:
                total_gas += gas_used
            if cost_eth != 'N/A':
                try:
                    total_cost += float(cost_eth)
                except:
                    pass
            if sync_time != 'N/A':
                try:
                    total_sync_time += float(sync_time.replace('s', ''))
                except:
                    pass
        
        # Check consistency
        if status == 'success':
            # Check data_consistency from metrics
            data_consistent = metrics.get('data_consistency', False)
            consistency = '✅ 100%' if data_consistent else '❌ Failed'
        elif status == 'failed_replication':
            consistency = '❌ Failed'
        elif status == 'error':
            consistency = '⚠️ Error'
        else:
            consistency = '⚠️ N/A'
        
        # Format battle ID
        battle_display = battle_id[:16] + '...' if len(battle_id) > 16 else battle_id
        
        # Format transaction hashes
        sepolia_display = sepolia_tx[:16] + '...' if len(sepolia_tx) > 16 else sepolia_tx
        base_display = base_tx[:16] + '...' if len(base_tx) > 16 else base_tx
        
        # Status formatting
        if status == 'failed_replication':
            status_display = '❌ Failed'
            failed_tests += 1
        elif status == 'error':
            status_display = '💥 Error'
            error_tests += 1
        elif status == 'passed' or 'success' in status.lower():
            status_display = '✅ Success'
            successful_tests += 1
        else:
            status_display = f'⚠️ {status}'
            failed_tests += 1
        
        print(f'{test_num:<6} {battle_display:<20} {sepolia_display:<20} {base_display:<20} {create_time:<12} {sync_time:<12} {consistency:<12} {gas_used:<10} {cost_eth:<12} {status_display:<15}')
    
    print('-' * 140)
    
    # Summary statistics
    total_tests = successful_tests + failed_tests + error_tests
    print(f'\n📊 SUMMARY STATISTICS')
    print('=' * 80)
    print(f'Total Tests: {total_tests}')
    print(f'Successful: {successful_tests}')
    print(f'Failed: {failed_tests}')
    print(f'Errors: {error_tests}')
    print(f'Success Rate: {(successful_tests/total_tests)*100:.1f}%' if total_tests > 0 else 'N/A')
    print(f'Average Sync Time: {total_sync_time/successful_tests:.2f}s' if successful_tests > 0 else 'N/A')
    print(f'Total Gas Used: {total_gas:,}')
    print(f'Total Cost: {total_cost:.8f} ETH')
    print(f'Average Cost per Test: {total_cost/total_tests:.8f} ETH' if total_tests > 0 else 'N/A')
    
    # Why Base TX shows N/A
    print(f'\n💡 WHY BASE TX SHOWS N/A:')
    print('=' * 80)
    print('Base TX shows N/A because:')
    print('1. Tests failed during replication step')
    print('2. SATP gateway may not be running')
    print('3. Insufficient funds for gas fees')
    print('4. Network connectivity issues')
    print('5. Manual replication not executed')
    
    # Explorer links
    print(f'\n🔗 EXPLORER LINKS')
    print('=' * 80)
    print('Sepolia Contract: https://sepolia.etherscan.io/address/0x17c3468D98b00bf24B6Bc1c67508d5D568E20cC6')
    print('Base Sepolia Contract: https://sepolia.basescan.org/address/0xF3a5cd8F0cA7D6BdfD8b36B04A951626Aa7DEDf1')
    
    # Show sample transactions if available
    if results['individual_tests']:
        first_test = results['individual_tests'][0]
        if first_test.get('creation_tx') and first_test.get('creation_tx') != 'N/A':
            tx_hash = first_test['creation_tx']
            print(f'Sample Sepolia TX: https://sepolia.etherscan.io/tx/{tx_hash}')
    
    print('=' * 140)

if __name__ == "__main__":
    analyze_latest_tests()
