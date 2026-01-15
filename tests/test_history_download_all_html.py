from app import app


def test_download_all_history_html():
    with app.test_client() as client:
        # Ensure there is at least one scan
        client.post('/api/scan/start', json={'targetOS': 'Linux'})

        r = client.get('/api/scan/history/download')
        assert r.status_code == 200
        assert r.headers.get('Content-Type', '').startswith('text/html')
        cd = r.headers.get('Content-Disposition', '')
        assert 'attachment' in cd and 'scan_history.html' in cd
        body = r.get_data(as_text=True)
        assert '<html' in body.lower()
        assert 'Security Baseline' in body or 'Scan' in body
