#!/usr/bin/env python3
"""
Generate a clean table of all test results
"""

import json
import os
from datetime import datetime

def generate_table():
    # Find the most recent test results file
    test_files = [f for f in os.listdir('test_results/') if f.endswith('.json') and 'multiple_tests_results' in f]
    if not test_files:
        print('❌ No test result files found')
        return
    
    # Get the most recent file
    latest_file = max(test_files, key=lambda x: os.path.getctime(f'test_results/{x}'))
    print(f'📁 Analyzing: {latest_file}\n')
    
    # Load the results
    with open(f'test_results/{latest_file}', 'r') as f:
        results = json.load(f)
    
    # Print header
    print("="*160)
    print(f"WEBBATTLES CROSS-CHAIN TEST RESULTS - {results['test_metadata']['num_tests']} Tests")
    print("="*160)
    print()
    
    # Table header
    header = f"{'Test#':<8}{'Battle ID':<68}{'Sepolia TX':<68}{'Base TX':<68}{'Create Time':<15}{'Sync Time':<15}{'Consistency':<15}"
    print(header)
    print("-"*160)
    
    # Table rows
    for test in results['individual_tests']:
        test_num = test.get('test_number', 'N/A')
        battle_id = test.get('battle_id', 'N/A')
        sepolia_tx = test.get('creation_tx', 'N/A')
        base_tx = test.get('replication_tx', 'N/A')
        
        # Get metrics
        metrics = test.get('metrics', {})
        create_time = f"{metrics.get('creation_time_seconds', 0):.2f}s" if metrics else 'N/A'
        sync_time = f"{metrics.get('total_sync_time_seconds', 0):.2f}s" if metrics else 'N/A'
        
        # Check consistency
        status = test.get('status', 'N/A')
        if status == 'success' and metrics:
            data_consistent = metrics.get('data_consistency', False)
            consistency = '✅ 100%' if data_consistent else '❌ Failed'
        else:
            consistency = '❌ Failed'
        
        # Print row
        row = f"{test_num:<8}{battle_id:<68}{sepolia_tx:<68}{base_tx:<68}{create_time:<15}{sync_time:<15}{consistency:<15}"
        print(row)
    
    print("-"*160)
    print()
    
    # Summary
    agg = results.get('aggregated_metrics', {})
    print("SUMMARY:")
    print(f"  Total Tests: {agg.get('total_tests_run', 0)}")
    print(f"  Successful: {agg.get('successful_tests', 0)}")
    print(f"  Success Rate: {agg.get('success_rate_percentage', 0):.1f}%")
    print(f"  Data Consistency: {agg.get('data_consistency_rate_percentage', 0):.1f}%")
    print(f"  Average Sync Time: {agg.get('avg_sync_time_seconds', 0):.2f}s")
    print()
    print("="*160)
    
    # Also save to CSV
    csv_filename = f'test_results/test_table_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    with open(csv_filename, 'w') as f:
        f.write("Test#,Battle ID,Sepolia TX,Base TX,Create Time (s),Sync Time (s),Consistency\n")
        for test in results['individual_tests']:
            test_num = test.get('test_number', 'N/A')
            battle_id = test.get('battle_id', 'N/A')
            sepolia_tx = test.get('creation_tx', 'N/A')
            base_tx = test.get('replication_tx', 'N/A')
            
            metrics = test.get('metrics', {})
            create_time = f"{metrics.get('creation_time_seconds', 0):.2f}" if metrics else 'N/A'
            sync_time = f"{metrics.get('total_sync_time_seconds', 0):.2f}" if metrics else 'N/A'
            
            status = test.get('status', 'N/A')
            if status == 'success' and metrics:
                data_consistent = metrics.get('data_consistency', False)
                consistency = '100%' if data_consistent else 'Failed'
            else:
                consistency = 'Failed'
            
            f.write(f"{test_num},{battle_id},{sepolia_tx},{base_tx},{create_time},{sync_time},{consistency}\n")
    
    print(f"✅ CSV file saved: {csv_filename}")

if __name__ == "__main__":
    generate_table()
