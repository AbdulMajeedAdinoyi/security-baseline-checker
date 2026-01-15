import json
from app import app


def test_scan_os_override_sets_fields(tmp_path, monkeypatch):
    # Use Flask test client
    with app.test_client() as client:
        # POST with targetOS override
        resp = client.post('/api/scan/start', json={'targetOS': 'Windows'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data is not None

        # Required OS fields are present
        assert 'os_used' in data
        assert 'detected_os' in data
        assert 'os_overridden' in data
        assert data['os_used'] == 'Windows'
        assert data['os_overridden'] is True

        # Also assert requested_target recorded
        assert data.get('requested_target') == 'Windows'

def test_history_includes_os_used(client=None):
    # Use Flask test client
    from app import app as flask_app
    with flask_app.test_client() as client:
        # Run a scan with override
        resp = client.post('/api/scan/start', json={'targetOS': 'Windows'})
        assert resp.status_code == 200

        # Fetch history and check the most recent entry
        hr = client.get('/api/scan/history?limit=1')
        assert hr.status_code == 200
        hist = hr.get_json()
        assert isinstance(hist, list) and len(hist) >= 1
        latest = hist[0]
        assert 'os_used' in latest
        assert latest['os_used'] == 'Windows'
        assert latest['os_overridden'] is True