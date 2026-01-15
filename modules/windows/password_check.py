import subprocess
import json
import shutil

class WindowsPasswordChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config

    def find_powershell(self):
        for cmd in ('powershell', 'pwsh'):
            if shutil.which(cmd):
                return cmd
        return None
    
    def check_password_policy(self):
        """Check Windows password policies"""
        ps_cmd = self.find_powershell()
        if not ps_cmd:
            return {
                'status': 'error',
                'category': 'Password Policy',
                'message': 'PowerShell/pwsh not available on this host. Install PowerShell or run this scan from a Windows host.'
            }

        try:
            # Get local users
            command = "Get-LocalUser | Select-Object Name, PasswordRequired | ConvertTo-Json"
            result = subprocess.run(
                [ps_cmd, "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                users = json.loads(result.stdout)
                return self.analyze_users(users)
            else:
                return {
                    'status': 'error',
                    'category': 'Password Policy',
                    'message': 'Failed to retrieve user information'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'category': 'Password Policy',
                'message': 'Command timed out'
            }
        except FileNotFoundError:
            return {
                'status': 'error',
                'category': 'Password Policy',
                'message': 'PowerShell executable not found on host.'
            }
        except Exception as e:
            return {
                'status': 'error',
                'category': 'Password Policy',
                'message': str(e)
            }
    
    def analyze_users(self, users):
        """Analyze user password requirements"""
        issues = []
        
        if isinstance(users, dict):
            users = [users]
        
        for user in users:
            if not user.get('PasswordRequired', True):
                issues.append({
                    'user': user['Name'],
                    'issue': 'Password not required',
                    'severity': 'High',
                    'remediation': 'Enable password requirement: Set-LocalUser -Name "{}" -PasswordNeverExpires $false'.format(user['Name'])
                })
        
        if issues:
            return {
                'status': 'non-compliant',
                'category': 'Password Policy',
                'issues': issues
            }
        
        return {
            'status': 'compliant',
            'category': 'Password Policy',
            'message': 'All users require passwords'
        }

def check(baseline):
    """Entry point for password check"""
    checker = WindowsPasswordChecker(baseline)
    return checker.check_password_policy()