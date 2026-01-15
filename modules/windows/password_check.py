import subprocess
import json

class WindowsPasswordChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config
    
    def check_password_policy(self):
        """Check Windows password policies"""
        try:
            # Get local users
            command = "Get-LocalUser | Select-Object Name, PasswordRequired | ConvertTo-Json"
            result = subprocess.run(
                ["powershell", "-Command", command],
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
                    'message': 'Failed to retrieve user information'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'status': 'error',
                'message': 'Command timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
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