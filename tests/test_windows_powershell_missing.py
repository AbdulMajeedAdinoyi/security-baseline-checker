from modules.windows import password_check, firewall_check, service_check


def test_password_check_reports_missing_powershell(monkeypatch):
    # Simulate missing powershell
    monkeypatch.setattr(password_check.shutil, 'which', lambda x: None)
    res = password_check.check({})
    assert res.get('status') == 'error'
    assert 'PowerShell' in res.get('message', '')


def test_firewall_check_reports_missing_powershell(monkeypatch):
    monkeypatch.setattr(firewall_check.shutil, 'which', lambda x: None)
    res = firewall_check.check({})
    assert res.get('status') == 'error'
    assert 'PowerShell' in res.get('message', '')


def test_services_check_reports_missing_powershell(monkeypatch):
    monkeypatch.setattr(service_check.shutil, 'which', lambda x: None)
    res = service_check.check({})
    assert res.get('status') == 'error'
    assert 'PowerShell' in res.get('message', '')
