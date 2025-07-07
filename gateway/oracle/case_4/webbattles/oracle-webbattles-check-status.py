#!/usr/bin/env python3

import requests
import json
from config import *

def check_oracle_status(task_id):
    """Check the status of an oracle task"""
    
    url = f"{GATEWAY_BASE_URL}/api/v1/@hyperledger/cactus-plugin-satp-hermes/oracle/status/{task_id}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"Oracle Task Status: {task_id}")
        print("-" * 60)
        
        if result.get("success"):
            data = result.get("data", {})
            print(f"Status: {data.get('status', 'Unknown')}")
            print(f"Task Type: {data.get('taskType', 'Unknown')}")
            print(f"Created: {data.get('createdAt', 'Unknown')}")
            print(f"Updated: {data.get('lastUpdated', 'Unknown')}")
            
            # Show execution history if available
            executions = data.get("executions", [])
            if executions:
                print(f"\nExecution History ({len(executions)} entries):")
                for i, execution in enumerate(executions[-5:]):  # Show last 5
                    print(f"  {i+1}. {execution.get('timestamp', 'Unknown')} - {execution.get('status', 'Unknown')}")
        else:
            print(f"Failed to get oracle status: {result.get('message', 'Unknown error')}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error checking oracle status: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def check_all_webbattles_oracles():
    """Check status of all registered WebBattles oracle tasks"""
    
    print("WEBBATTLES ORACLE STATUS CHECK")
    print("=" * 60)
    
    print("\nSync Oracle Task:")
    check_oracle_status(SYNC_TASK_ID)
    
    print("\nReplication Oracle Task:")
    check_oracle_status(REPLICATION_TASK_ID)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        task_id = sys.argv[1]
        print(f"Checking specific oracle task: {task_id}")
        check_oracle_status(task_id)
    else:
        check_all_webbattles_oracles() 
        