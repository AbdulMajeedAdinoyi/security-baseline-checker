import subprocess
import json

class LinuxServiceChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config

    def check_services(self):
        """Check that services listed under baseline.services.disabled are stopped/disabled (systemd)"""
        try:
            disabled = self.baseline.get('services', {}).get('disabled', [])
            issues = []

            for svc in disabled:
                try:
                    # Check systemd active state
                    result = subprocess.run(
                        ["systemctl", "is-active", svc],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )

                    status = result.stdout.strip()
                    if status and status != 'inactive' and status != 'failed':
                        issues.append({
                            'service': svc,
                            'issue': f'Service {svc} is active (state: {status})',
                            'severity': 'High',
                            'remediation': f'Disable and stop service: systemctl disable --now {svc}'
                        })
                except Exception:
                    issues.append({
                        'service': svc,
                        'issue': f'Failed to query service {svc}',
                        'severity': 'Medium',
                        'remediation': f'Investigate service status for {svc}'
                    })

            if issues:
                return {
                    'status': 'non-compliant',
                    'category': 'Services',
                    'issues': issues
                }

            return {
                'status': 'compliant',
                'category': 'Services',
                'message': 'Required services are disabled or not present'
            }
        except Exception as e:
            return {
                'status': 'error',
                'category': 'Services',
                'message': str(e)
            }


def check(baseline):
    checker = LinuxServiceChecker(baseline)
    return checker.check_services()
