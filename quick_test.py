#!/usr/bin/env python3
"""Test the scanner directly"""

from app import SecurityBaselineScanner

print("Testing SecurityBaselineScanner with Windows...")
scanner = SecurityBaselineScanner(os_override='Windows')
results = scanner.run_scan()

print(f"Scan completed!")
print(f"Score: {results.get('score')}")
print(f"Total checks: {results.get('total_checks')}")
print(f"Compliant: {results.get('compliant_count')}")
print(f"Non-compliant: {results.get('non_compliant_count')}")
print(f"OS used: {results.get('os_used')}")
print(f"Duration: {results.get('duration')}s")
print(f"Checks performed: {len(results.get('checks', []))}")

