#!/bin/bash
# Quick command to analyze latest test results
cd "$(dirname "$0")"
python3 test-results-analyzer.py
