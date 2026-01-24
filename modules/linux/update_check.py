import subprocess

class LinuxUpdateChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config

    def check_updates(self):
        """Check if Linux has pending updates"""
        try:
            # Try apt-get (Debian/Ubuntu)
            if self._command_exists('apt-get'):
                return self._check_apt_updates()
            # Try yum (RHEL/CentOS)
            elif self._command_exists('yum'):
                return self._check_yum_updates()
            # Try dnf (Fedora)
            elif self._command_exists('dnf'):
                return self._check_dnf_updates()
            else:
                return {
                    'status': 'warning',
                    'category': 'System Updates',
                    'message': 'Unable to determine package manager (apt, yum, or dnf not found)'
                }
        except Exception as e:
            return {
                'status': 'error',
                'category': 'System Updates',
                'message': f'Error checking updates: {str(e)}'
            }

    def _check_apt_updates(self):
        """Check for apt-get updates"""
        try:
            # Update package list (requires sudo)
            result = subprocess.run(
                ['sudo', 'apt-get', 'update'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Check for upgradeable packages
            result = subprocess.run(
                ['apt-get', '-s', 'upgrade'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            upgradeable = result.stdout.count('upgraded')
            
            if upgradeable > 0:
                return {
                    'status': 'non-compliant',
                    'category': 'System Updates',
                    'issues': [{
                        'issue': f'System has {upgradeable} packages available for upgrade',
                        'severity': 'Medium',
                        'remediation': 'Install updates: sudo apt-get update && sudo apt-get upgrade'
                    }]
                }
            else:
                return {
                    'status': 'compliant',
                    'category': 'System Updates',
                    'message': 'System is up to date with all security patches installed'
                }
        except Exception as e:
            return {
                'status': 'warning',
                'category': 'System Updates',
                'message': f'Could not check apt updates: {str(e)}'
            }

    def _check_yum_updates(self):
        """Check for yum updates"""
        try:
            result = subprocess.run(
                ['yum', 'check-update'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # yum check-update returns non-zero if updates are available
            if result.returncode == 100:
                updates_available = len([l for l in result.stdout.split('\n') if l.strip() and not l.startswith(' ')])
                return {
                    'status': 'non-compliant',
                    'category': 'System Updates',
                    'issues': [{
                        'issue': f'System has {updates_available} packages available for update',
                        'severity': 'Medium',
                        'remediation': 'Install updates: sudo yum update'
                    }]
                }
            else:
                return {
                    'status': 'compliant',
                    'category': 'System Updates',
                    'message': 'System is up to date'
                }
        except Exception as e:
            return {
                'status': 'warning',
                'category': 'System Updates',
                'message': f'Could not check yum updates: {str(e)}'
            }

    def _check_dnf_updates(self):
        """Check for dnf updates (Fedora)"""
        try:
            result = subprocess.run(
                ['dnf', 'check-update'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 100:
                updates_available = len([l for l in result.stdout.split('\n') if l.strip() and not l.startswith(' ')])
                return {
                    'status': 'non-compliant',
                    'category': 'System Updates',
                    'issues': [{
                        'issue': f'System has {updates_available} packages available for update',
                        'severity': 'Medium',
                        'remediation': 'Install updates: sudo dnf upgrade'
                    }]
                }
            else:
                return {
                    'status': 'compliant',
                    'category': 'System Updates',
                    'message': 'System is up to date'
                }
        except Exception as e:
            return {
                'status': 'warning',
                'category': 'System Updates',
                'message': f'Could not check dnf updates: {str(e)}'
            }

    def _command_exists(self, cmd):
        """Check if a command exists in PATH"""
        return subprocess.call(
            ['which', cmd],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        ) == 0

def check(baseline):
    """Entry point for Linux update check"""
    checker = LinuxUpdateChecker(baseline)
    return checker.check_updates()
