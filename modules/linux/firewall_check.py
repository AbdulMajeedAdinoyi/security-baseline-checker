import subprocess
import os

class LinuxFirewallChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config
    
    def check_firewall(self):
        """Check Linux firewall status (ufw or firewalld)"""
        try:
            # Check if ufw is available
            if self.command_exists('ufw'):
                return self.check_ufw()
            # Check if firewalld is available
            elif self.command_exists('firewall-cmd'):
                return self.check_firewalld()
            else:
                return {
                    'status': 'warning',
                    'category': 'Firewall',
                    'message': 'No supported firewall (ufw/firewalld) detected'
                }
        except Exception as e:
            return {
                'status': 'error',
                'category': 'Firewall',
                'message': str(e)
            }
    
    def check_ufw(self):
        """Check UFW firewall status"""
        try:
            result = subprocess.run(
                ['sudo', 'ufw', 'status'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if 'Status: active' in result.stdout:
                return {
                    'status': 'compliant',
                    'category': 'Firewall',
                    'message': 'UFW firewall is active'
                }
            else:
                return {
                    'status': 'non-compliant',
                    'category': 'Firewall',
                    'issues': [{
                        'issue': 'UFW firewall is not active',
                        'severity': 'Critical',
                        'remediation': 'Enable UFW: sudo ufw enable'
                    }]
                }
        except Exception as e:
            return {
                'status': 'error',
                'category': 'Firewall',
                'message': f'Error checking UFW: {str(e)}'
            }
    
    def check_firewalld(self):
        """Check firewalld status"""
        try:
            result = subprocess.run(
                ['sudo', 'firewall-cmd', '--state'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if 'running' in result.stdout.lower():
                return {
                    'status': 'compliant',
                    'category': 'Firewall',
                    'message': 'Firewalld is running'
                }
            else:
                return {
                    'status': 'non-compliant',
                    'category': 'Firewall',
                    'issues': [{
                        'issue': 'Firewalld is not running',
                        'severity': 'Critical',
                        'remediation': 'Start firewalld: sudo systemctl start firewalld'
                    }]
                }
        except Exception as e:
            return {
                'status': 'error',
                'category': 'Firewall',
                'message': f'Error checking firewalld: {str(e)}'
            }
    
    def command_exists(self, command):
        """Check if a command exists"""
        return subprocess.call(
            ['which', command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ) == 0

def check(baseline):
    """Entry point for firewall check"""
    checker = LinuxFirewallChecker(baseline)
    return checker.check_firewall()