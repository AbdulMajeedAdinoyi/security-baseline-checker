import subprocess
import json
import shutil

class WindowsFirewallChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config

    def find_powershell(self):
        for cmd in ('powershell', 'pwsh'):
            if shutil.which(cmd):
                return cmd
        return None
    
    def check_firewall(self):
        """Check Windows Firewall status for all profiles"""
        ps_cmd = self.find_powershell()
        if not ps_cmd:
            return {
                'status': 'error',
                'category': 'Firewall',
                'message': 'PowerShell/pwsh not available on this host. Install PowerShell or run this scan from a Windows host.'
            }

        try:
            issues = []
            
            profiles = ['Domain', 'Private', 'Public']
            
            for profile in profiles:
                status = self.check_profile(profile, ps_cmd)
                if status and status.get('enabled') == False:
                    issues.append({
                        'profile': profile,
                        'issue': f'{profile} firewall is disabled',
                        'severity': 'Critical',
                        'remediation': f'Enable {profile} firewall: Set-NetFirewallProfile -Profile {profile} -Enabled True'
                    })
            
            if issues:
                return {
                    'status': 'non-compliant',
                    'category': 'Firewall',
                    'issues': issues
                }
            
            return {
                'status': 'compliant',
                'category': 'Firewall',
                'message': 'All firewall profiles are enabled'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'category': 'Firewall',
                'message': str(e)
            }
    
    def check_profile(self, profile, ps_cmd):
        """Check specific firewall profile status"""
        try:
            command = f"Get-NetFirewallProfile -Profile {profile} | Select-Object Name, Enabled | ConvertTo-Json"
            result = subprocess.run(
                [ps_cmd, "-Command", command],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    'name': data.get('Name'),
                    'enabled': data.get('Enabled')
                }
        except Exception:
            return None

def check(baseline):
    """Entry point for firewall check"""
    checker = WindowsFirewallChecker(baseline)
    return checker.check_firewall()