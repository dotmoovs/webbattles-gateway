#!/usr/bin/env python3

import re
import os

def update_config_variable(variable_name, new_value):
    """
    Update a variable in config.py with a new value
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    
    # Read the current config
    with open(config_path, 'r') as file:
        content = file.read()
    
    # Create the pattern to match the variable assignment
    # Handle both string and non-string values
    if isinstance(new_value, str):
        pattern = rf'^({variable_name}\s*=\s*)["\'].*["\']'
        replacement = rf'\1"{new_value}"'
    else:
        pattern = rf'^({variable_name}\s*=\s*).*'
        replacement = rf'\1{new_value}'
    
    # Update the content
    updated_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
    
    # Write back to file
    with open(config_path, 'w') as file:
        file.write(updated_content)
    
    print(f"Updated {variable_name} = {new_value}")

def update_multiple_config_variables(updates):
    """
    Update multiple variables in config.py
    updates: dict with variable_name -> new_value
    """
    for variable_name, new_value in updates.items():
        update_config_variable(variable_name, new_value) 