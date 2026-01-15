from flask import Flask, render_template, jsonify, request, send_file
import json
import time
from datetime import datetime
from modules.platform_detector import PlatformDetector
from database.db_manager import DatabaseManager

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
db_manager = DatabaseManager()

class SecurityBaselineScanner:
    def __init__(self, os_override=None):
        self.baseline = self.load_config('config/baseline.json')
        self.platform = PlatformDetector()
        self.os_override = os_override  # allow manual OS selection override
        self.results = {
            'scan_id': None,
            'checks': [],
            'score': 0,
            'os_type': None,
            'detected_os': None,
            'os_used': None,
            'os_overridden': False,
            'requested_target': None,
            'duration': 0
        }
    
    def load_config(self, path):
        """Load baseline configuration from JSON file"""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
    
    def run_scan(self):
        """Execute complete security baseline scan"""
        start_time = time.time()
        
        print("Starting security baseline scan...")
        
        # Detect platform for information purposes and honor override when provided
        detected = self.platform.detect_platform()
        self.results['detected_os'] = detected or 'Unknown'
        self.results['requested_target'] = self.os_override

        if self.os_override:
            os_type = self.os_override
            self.results['os_overridden'] = True
            print(f"Using manual OS override: {os_type}")
        else:
            if not detected:
                return {'error': 'Unsupported operating system'}
            os_type = detected
            self.results['os_overridden'] = False
            print(f"Detected platform: {os_type}")

        self.results['os_type'] = os_type
        self.results['os_used'] = os_type
        
        # Load appropriate modules
        try:
            powershell_available = None
            if os_type == "Windows":
                import shutil
                powershell_available = bool(shutil.which('powershell') or shutil.which('pwsh'))
                from modules.windows import password_check, firewall_check, service_check
                modules = {
                    'Password Policy': password_check,
                    'Firewall': firewall_check,
                    'Services': service_check
                }
            else:  # Linux
                from modules.linux import password_check, firewall_check, service_check, permission_check
                modules = {
                    'Password Policy': password_check,
                    'Firewall': firewall_check,
                    'Services': service_check,
                    'File Permissions': permission_check
                }
        except Exception as e:
            return {'error': f'Failed to load checking modules: {str(e)}'}

        # Record powershell availability if relevant
        self.results['powershell_available'] = powershell_available
        
        # Run each check
        for name, module in modules.items():
            print(f"Running {name} check...")
            try:
                result = module.check(self.baseline)
                result['name'] = name
                self.results['checks'].append(result)
            except Exception as e:
                print(f"Error in {name} check: {e}")
                self.results['checks'].append({
                    'name': name,
                    'status': 'error',
                    'category': name,
                    'message': str(e)
                })
        
        # Calculate compliance score
        self.calculate_score()
        
        # Calculate duration
        self.results['duration'] = int(time.time() - start_time)
        
        # Save to database
        try:
            scan_id = db_manager.save_scan(self.results)
            self.results['scan_id'] = scan_id
        except Exception as e:
            print(f"Failed to save scan results: {e}")
        
        return self.results
    
    def calculate_score(self):
        """Calculate overall compliance score"""
        total = len(self.results['checks'])
        compliant = sum(1 for c in self.results['checks'] 
                       if c.get('status') == 'compliant')
        
        if total > 0:
            self.results['score'] = round((compliant / total) * 100, 2)
            self.results['total_checks'] = total
            self.results['compliant_count'] = compliant
            self.results['non_compliant_count'] = total - compliant
            self.results['warning_count'] = 0
        else:
            self.results['score'] = 0

# Flask Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/scan')
def scan_page():
    """Scan initiation page"""
    return render_template('scan.html')

@app.route('/history')
def history_page():
    """Scan history page"""
    return render_template('history.html')

@app.route('/api/scan/start', methods=['POST'])
def start_scan():
    """API endpoint to start a new scan"""
    try:
        data = request.get_json(silent=True) or {}
        target_os = data.get('targetOS')
        if target_os and target_os not in ['Windows', 'Linux']:
            return jsonify({'error': 'Invalid targetOS. Must be "Windows" or "Linux"'}), 400

        scanner = SecurityBaselineScanner(os_override=target_os)
        results = scanner.run_scan()
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/history')
def get_history():
    """API endpoint to get scan history"""
    try:
        limit = request.args.get('limit', 10, type=int)
        history = db_manager.get_scan_history(limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/history/clear', methods=['POST'])
def clear_history():
    """Clear all scan history (use with caution)"""
    try:
        db_manager.delete_all_scans()
        return jsonify({'status': 'ok'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/history/download')
def download_history_html():
    """Return an HTML file containing all scan history"""
    try:
        # get all history entries and expand to full scans
        history = db_manager.get_scan_history(10000)
        scans = []
        for entry in history:
            full = db_manager.get_scan_by_id(entry['scan_id'])
            if full:
                scans.append(full)
        html = render_template('history_report.html', scans=scans)
        resp = app.response_class(html, mimetype='text/html')
        resp.headers['Content-Disposition'] = f'attachment; filename=scan_history.html'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<int:scan_id>/download/html')
def download_scan_html(scan_id):
    """Return a scan result as downloadable HTML report"""
    try:
        scan = db_manager.get_scan_by_id(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        html = render_template('scan_report.html', scan=scan)
        resp = app.response_class(html, mimetype='text/html')
        resp.headers['Content-Disposition'] = f'attachment; filename=scan_{scan_id}.html'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan/<int:scan_id>/download')
def download_scan(scan_id):
    """Return a scan result as a downloadable JSON file"""
    try:
        scan = db_manager.get_scan_by_id(scan_id)
        if not scan:
            return jsonify({'error': 'Scan not found'}), 404
        resp = jsonify(scan)
        resp.headers['Content-Disposition'] = f'attachment; filename=scan_{scan_id}.json'
        return resp
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/system/info')
def system_info():
    """API endpoint to get system information"""
    try:
        import shutil
        detector = PlatformDetector()
        os_type = detector.detect_platform()
        details = detector.get_os_details()

        # Check for PowerShell availability on the host (powershell or pwsh)
        ps_available = bool(shutil.which('powershell') or shutil.which('pwsh'))

        return jsonify({
            'os_type': os_type,
            'details': details,
            'powershell_available': ps_available
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    print("=" * 60)
    print("Security Baseline Compliance Checker")
    print("=" * 60)
    print("Starting web server...")
    print("Open your browser and navigate to: http://127.0.0.1:5000")
    print("=" * 60)
    
    # Use debug mode only in development
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=int(os.getenv('PORT', 5000)))