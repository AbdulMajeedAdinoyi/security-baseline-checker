import subprocess
import json

class WindowsServiceChecker:
    def __init__(self, baseline_config):
        self.baseline = baseline_config

    def check_services(self):
        """Check that services listed under baseline.services.disabled are stopped/disabled"""
        try:
            disabled = self.baseline.get('services', {}).get('disabled', [])
            issues = []

            for svc in disabled:
                try:
                    command = f"Get-Service -Name '{svc}' -ErrorAction SilentlyContinue | Select-Object Name, Status | ConvertTo-Json"
                    result = subprocess.run(
                        ["powershell", "-Command", command],
                        capture_output=True,
                        text=True,
                        timeout=20
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        data = json.loads(result.stdout)
                        # Normalize list/dict
                        if isinstance(data, list):
                            data = data[0]

                        status = (data.get('Status') or '').lower()
                        if status not in ('stopped', 'stopping'):
                            issues.append({
                                'service': svc,
                                'issue': f'Service {svc} is running (status: {status})',
                                'severity': 'High',
                                'remediation': f'Stop and disable service: Stop-Service -Name "{svc}"; Set-Service -Name "{svc}" -StartupType Disabled'
                            })
                    else:
                        # If the service cannot be found, skip it (treat as compliant)
                        continue
                except Exception:
                    # Non-fatal for a single service
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
    checker = WindowsServiceChecker(baseline)
    return checker.check_services()
