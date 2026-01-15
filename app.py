from flask import Flask, render_template, jsonify, request, send_file
import json
import time
from datetime import datetime
from modules.platform_detector import PlatformDetector
from database.db_manager import DatabaseManager

app = Flask(__name__, template_folder='web/templates', static_folder='web/static')
db_manager = DatabaseManager()

class SecurityBaselineScanner:
    def __init__(self):
        self.baseline = self.load_config('config/baseline.json')
        self.platform = PlatformDetector()
        self.results = {
            'scan_id': None,
            'checks': [],
            'score': 0,
            'os_type': None,
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
        
        # Detect platform
        os_type = self.platform.detect_platform()
        if not os_type:
            return {'error': 'Unsupported operating system'}
        
        print(f"Detected platform: {os_type}")
        self.results['os_type'] = os_type
        
        # Load appropriate modules
        try:
            if os_type == "Windows":
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
        scanner = SecurityBaselineScanner()
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

@app.route('/api/system/info')
def system_info():
    """API endpoint to get system information"""
    try:
        detector = PlatformDetector()
        os_type = detector.detect_platform()
        details = detector.get_os_details()
        return jsonify({
            'os_type': os_type,
            'details': details
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