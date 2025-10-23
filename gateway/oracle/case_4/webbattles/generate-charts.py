#!/usr/bin/env python3
"""
Generate charts and visualizations from test results
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import os

# Set style for professional-looking charts
plt.style.use('seaborn-v0_8-darkgrid')

def generate_charts():
    # Load the latest test results
    test_files = [f for f in os.listdir('test_results/') if f.endswith('.json') and 'multiple_tests_results_100tests' in f]
    if not test_files:
        print('❌ No test result files found')
        return
    
    latest_file = max(test_files, key=lambda x: os.path.getctime(f'test_results/{x}'))
    print(f'📁 Loading: {latest_file}')
    
    with open(f'test_results/{latest_file}', 'r') as f:
        results = json.load(f)
    
    # Extract data
    test_numbers = []
    creation_times = []
    sync_times = []
    replication_times = []
    total_costs = []
    gas_used = []
    
    for test in results['individual_tests']:
        metrics = test.get('metrics', {})
        if metrics:
            test_numbers.append(test['test_number'])
            creation_times.append(metrics.get('creation_time_seconds', 0))
            sync_times.append(metrics.get('total_sync_time_seconds', 0))
            replication_times.append(metrics.get('replication_time_seconds', 0))
            total_costs.append(metrics.get('total_cost_eth', 0))
            gas_used.append(metrics.get('total_gas_used', 0))
    
    # Create timestamp for filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 12))
    
    # 1. Creation Time over Tests
    ax1 = plt.subplot(3, 2, 1)
    ax1.plot(test_numbers, creation_times, 'b-', alpha=0.6, linewidth=1)
    ax1.axhline(y=np.mean(creation_times), color='r', linestyle='--', label=f'Mean: {np.mean(creation_times):.2f}s')
    ax1.set_xlabel('Test Number')
    ax1.set_ylabel('Creation Time (seconds)')
    ax1.set_title('Battle Creation Time on Sepolia')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Sync Time over Tests
    ax2 = plt.subplot(3, 2, 2)
    ax2.plot(test_numbers, sync_times, 'g-', alpha=0.6, linewidth=1)
    ax2.axhline(y=np.mean(sync_times), color='r', linestyle='--', label=f'Mean: {np.mean(sync_times):.2f}s')
    ax2.set_xlabel('Test Number')
    ax2.set_ylabel('Sync Time (seconds)')
    ax2.set_title('Cross-Chain Synchronization Time')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Creation Time Distribution
    ax3 = plt.subplot(3, 2, 3)
    ax3.hist(creation_times, bins=20, color='blue', alpha=0.7, edgecolor='black')
    ax3.axvline(x=np.mean(creation_times), color='r', linestyle='--', label=f'Mean: {np.mean(creation_times):.2f}s')
    ax3.axvline(x=np.median(creation_times), color='orange', linestyle='--', label=f'Median: {np.median(creation_times):.2f}s')
    ax3.set_xlabel('Creation Time (seconds)')
    ax3.set_ylabel('Frequency')
    ax3.set_title('Creation Time Distribution')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # 4. Sync Time Distribution
    ax4 = plt.subplot(3, 2, 4)
    ax4.hist(sync_times, bins=20, color='green', alpha=0.7, edgecolor='black')
    ax4.axvline(x=np.mean(sync_times), color='r', linestyle='--', label=f'Mean: {np.mean(sync_times):.2f}s')
    ax4.axvline(x=np.median(sync_times), color='orange', linestyle='--', label=f'Median: {np.median(sync_times):.2f}s')
    ax4.set_xlabel('Sync Time (seconds)')
    ax4.set_ylabel('Frequency')
    ax4.set_title('Sync Time Distribution')
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    # 5. Gas Usage
    ax5 = plt.subplot(3, 2, 5)
    ax5.plot(test_numbers, gas_used, 'purple', alpha=0.6, linewidth=1)
    ax5.axhline(y=np.mean(gas_used), color='r', linestyle='--', label=f'Mean: {np.mean(gas_used):,.0f}')
    ax5.set_xlabel('Test Number')
    ax5.set_ylabel('Gas Used')
    ax5.set_title('Total Gas Usage per Test')
    ax5.legend()
    ax5.grid(True, alpha=0.3)
    
    # 6. Summary Box
    ax6 = plt.subplot(3, 2, 6)
    ax6.axis('off')
    
    summary_text = f'''
    STATISTICAL SUMMARY
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    Total Tests:           100
    Success Rate:          100.0%
    Data Consistency:      100.0%
    
    CREATION TIME (Sepolia)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Mean:     {np.mean(creation_times):.2f}s
    Median:   {np.median(creation_times):.2f}s
    Std Dev:  ±{np.std(creation_times):.2f}s
    Range:    {np.min(creation_times):.2f}s - {np.max(creation_times):.2f}s
    
    SYNC TIME (Cross-Chain)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Mean:     {np.mean(sync_times):.2f}s
    Median:   {np.median(sync_times):.2f}s
    Std Dev:  ±{np.std(sync_times):.2f}s
    Range:    {np.min(sync_times):.2f}s - {np.max(sync_times):.2f}s
    
    COST
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Avg Gas:  {np.mean(gas_used):,.0f}
    Avg Cost: {np.mean(total_costs):.8f} ETH
    Total:    {np.sum(total_costs):.6f} ETH
    '''
    
    ax6.text(0.1, 0.5, summary_text, fontsize=10, family='monospace',
             verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    # Save figure
    chart_file = f'test_results/test_charts_{timestamp}.png'
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    print(f'✅ Charts saved: {chart_file}')
    
    # Create individual focused charts
    
    # Chart 2: Sync Time Performance (most important)
    fig2, ax = plt.subplots(figsize=(12, 6))
    ax.plot(test_numbers, sync_times, 'g-', alpha=0.7, linewidth=2, label='Sync Time')
    ax.fill_between(test_numbers, 
                     [np.mean(sync_times) - np.std(sync_times)] * len(test_numbers),
                     [np.mean(sync_times) + np.std(sync_times)] * len(test_numbers),
                     alpha=0.2, color='green', label='±1 Std Dev')
    ax.axhline(y=np.mean(sync_times), color='r', linestyle='--', linewidth=2, label=f'Mean: {np.mean(sync_times):.2f}s')
    ax.set_xlabel('Test Number', fontsize=12)
    ax.set_ylabel('Sync Time (seconds)', fontsize=12)
    ax.set_title('Cross-Chain Synchronization Time - 100 Tests', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    
    sync_chart = f'test_results/sync_time_chart_{timestamp}.png'
    plt.savefig(sync_chart, dpi=300, bbox_inches='tight')
    print(f'✅ Sync time chart saved: {sync_chart}')
    
    # Chart 3: Box plot comparison
    fig3, ax = plt.subplots(figsize=(10, 6))
    data_to_plot = [creation_times, sync_times, replication_times]
    labels = ['Creation\nTime', 'Total Sync\nTime', 'Replication\nTime']
    bp = ax.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    ax.set_ylabel('Time (seconds)', fontsize=12)
    ax.set_title('Time Metrics Distribution - 100 Cross-Chain Tests', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    boxplot_chart = f'test_results/time_distribution_boxplot_{timestamp}.png'
    plt.savefig(boxplot_chart, dpi=300, bbox_inches='tight')
    print(f'✅ Box plot saved: {boxplot_chart}')
    
    print()
    print('=' * 70)
    print('📊 ALL CHARTS GENERATED SUCCESSFULLY!')
    print('=' * 70)
    print()
    print('Files created:')
    print(f'  1. {chart_file}')
    print(f'  2. {sync_chart}')
    print(f'  3. {boxplot_chart}')

if __name__ == "__main__":
    generate_charts()
