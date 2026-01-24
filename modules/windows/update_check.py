import subprocess
import os

class WindowsUpdateChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config

    def check_updates(self):
        """Check if Windows has pending updates"""
        try:
            # Use PowerShell to check Windows Update status
            command = """
            $updates = Get-WmiObject -Class Win32_QuickFixEngineering | Measure-Object
            $pendingUpdates = Get-ChildItem 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Component Based Servicing\\Packages' -ErrorAction SilentlyContinue | Where-Object {$_.PSChildName -match 'pending'} | Measure-Object
            
            $result = @{
                'InstalledUpdates' = $updates.Count
                'PendingUpdates' = $pendingUpdates.Count
                'HasPendingUpdates' = $pendingUpdates.Count -gt 0
            }
            $result | ConvertTo-Json
            """
            
            result = subprocess.run(
                ['powershell', '-Command', command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                try:
                    import json
                    data = json.loads(result.stdout)
                    
                    if data.get('HasPendingUpdates'):
                        return {
                            'status': 'non-compliant',
                            'category': 'System Updates',
                            'issues': [{
                                'issue': f"System has {data.get('PendingUpdates', '?')} pending updates",
                                'severity': 'Medium',
                                'remediation': 'Install pending updates: Settings > Update & Security > Windows Update > Check for updates'
                            }]
                        }
                    else:
                        return {
                            'status': 'compliant',
                            'category': 'System Updates',
                            'message': f"System is up to date with {data.get('InstalledUpdates', 0)} updates installed"
                        }
                except:
                    return {
                        'status': 'warning',
                        'category': 'System Updates',
                        'message': 'Could not parse update status'
                    }
            else:
                return {
                    'status': 'warning',
                    'category': 'System Updates',
                    'message': 'Unable to check Windows updates'
                }
        except Exception as e:
            return {
                'status': 'error',
                'category': 'System Updates',
                'message': f'Error checking updates: {str(e)}'
            }

def check(baseline):
    """Entry point for Windows update check"""
    checker = WindowsUpdateChecker(baseline)
    return checker.check_updates()
