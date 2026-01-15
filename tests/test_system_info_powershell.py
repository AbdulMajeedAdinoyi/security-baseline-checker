from app import app
import json


def test_system_info_reports_powershell(monkeypatch):
    # Simulate that neither powershell nor pwsh is available
    import shutil
    monkeypatch.setattr(shutil, 'which', lambda x: None)

    with app.test_client() as client:
        r = client.get('/api/system/info')
        assert r.status_code == 200
        data = r.get_json()
        assert 'powershell_available' in data
        assert data['powershell_available'] is False


def test_scan_with_windows_override_and_missing_powershell(monkeypatch):
    # Simulate missing powershell
    import shutil
    monkeypatch.setattr(shutil, 'which', lambda x: None)

    with app.test_client() as client:
        # POST a Windows scan; checks should return friendly PowerShell error statuses
        r = client.post('/api/scan/start', json={'targetOS': 'Windows'})
        assert r.status_code == 200
        data = r.get_json()
        assert data is not None

        # Response should include explicit powershell_available flag set to False
        assert 'powershell_available' in data
        assert data['powershell_available'] is False

        # At least one check should report an error mentioning PowerShell
        errors = [c for c in data.get('checks', []) if c.get('status') == 'error']
        assert any('PowerShell' in (c.get('message') or '') for c in errors)

        # The saved history should have powershell_available == False for the latest scan
        hr = client.get('/api/scan/history?limit=1')
        hist = hr.get_json()
        assert hist and isinstance(hist, list)
        latest = hist[0]
        assert latest.get('powershell_available') is False
