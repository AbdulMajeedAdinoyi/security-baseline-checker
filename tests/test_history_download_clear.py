from app import app


def test_download_scan_and_clear_history():
    with app.test_client() as client:
        # Create a scan (use Linux to avoid PS issues)
        resp = client.post('/api/scan/start', json={'targetOS': 'Linux'})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data and 'scan_id' in data
        scan_id = data['scan_id']

        # Download the scan
        dl = client.get(f'/api/scan/{scan_id}/download')
        assert dl.status_code == 200
        dl_json = dl.get_json()
        assert dl_json and dl_json.get('scan_id') == scan_id

        # Clear history
        cr = client.post('/api/scan/history/clear')
        assert cr.status_code == 200
        cr_json = cr.get_json()
        assert cr_json.get('status') == 'ok'

        # Ensure history is empty
        hr = client.get('/api/scan/history')
        assert hr.status_code == 200
        assert hr.get_json() == []
