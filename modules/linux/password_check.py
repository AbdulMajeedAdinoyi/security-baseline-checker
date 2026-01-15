import re
import os

class LinuxPasswordChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config
    
    def check_password_policy(self):
        """Check Linux password policies"""
        try:
            issues = []
            
            # Check minimum password length
            min_length_issue = self.check_min_length()
            if min_length_issue:
                issues.append(min_length_issue)
            
            # Check password complexity
            complexity_issue = self.check_complexity()
            if complexity_issue:
                issues.append(complexity_issue)
            
            if issues:
                return {
                    'status': 'non-compliant',
                    'category': 'Password Policy',
                    'issues': issues
                }
            
            return {
                'status': 'compliant',
                'category': 'Password Policy',
                'message': 'Password policies meet baseline requirements'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'category': 'Password Policy',
                'message': str(e)
            }
    
    def check_min_length(self):
        """Check minimum password length from /etc/login.defs"""
        try:
            if os.path.exists('/etc/login.defs'):
                with open('/etc/login.defs', 'r') as f:
                    content = f.read()
                    match = re.search(r'PASS_MIN_LEN\s+(\d+)', content)
                    if match:
                        min_len = int(match.group(1))
                        required_len = self.baseline.get('password_policy', {}).get('min_length', 8)
                        
                        if min_len < required_len:
                            return {
                                'issue': f'Minimum password length is {min_len}, required is {required_len}',
                                'severity': 'High',
                                'remediation': f'Edit /etc/login.defs and set PASS_MIN_LEN {required_len}'
                            }
        except Exception as e:
            return {
                'issue': f'Could not check minimum password length: {str(e)}',
                'severity': 'Medium',
                'remediation': 'Check /etc/login.defs file permissions'
            }
        return None
    
    def check_complexity(self):
        """Check password complexity requirements"""
        try:
            pam_file = '/etc/pam.d/common-password'
            if os.path.exists(pam_file):
                with open(pam_file, 'r') as f:
                    content = f.read()
                    if 'pam_pwquality' not in content and 'pam_cracklib' not in content:
                        return {
                            'issue': 'Password complexity not enforced',
                            'severity': 'High',
                            'remediation': 'Install and configure libpam-pwquality package'
                        }
        except Exception as e:
            return {
                'issue': f'Could not check password complexity: {str(e)}',
                'severity': 'Medium',
                'remediation': 'Check PAM configuration file permissions'
            }
        return None

def check(baseline):
    """Entry point for password check"""
    checker = LinuxPasswordChecker(baseline)
    return checker.check_password_policy()