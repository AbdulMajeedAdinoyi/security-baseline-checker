import json
import time
from datetime import datetime
from modules.platform_detector import PlatformDetector
from database.db_manager import DatabaseManager

class SecurityBaselineScanner:
    def __init__(self, config_path='config/baseline.json'):
        self.baseline = self.load_config(config_path)
        self.platform = PlatformDetector()
        self.db_manager = DatabaseManager()
        self.results = {
            'scan_id': None,
            'scan_date': None,
            'os_type': None,
            'checks': [],
            'score': 0,
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
        print("=" * 60)
        print("Starting Security Baseline Scan...")
        print("=" * 60)
        
        # Detect platform
        os_type = self.platform.detect_platform()
        if not os_type:
            return {
                'error': 'Unsupported operating system',
                'status': 'failed'
            }
        
        print(f"Detected OS: {os_type}")
        self.results['os_type'] = os_type
        self.results['scan_date'] = datetime.now().isoformat()
        
        # Load appropriate modules
        print("\nLoading security check modules...")
        modules = self.load_platform_modules(os_type)
        
        # Run each check
        print("\nExecuting security checks:")
        print("-" * 60)
        
        for name, module in modules.items():
            print(f"Running {name} check...", end=" ")
            try:
                result = module.check(self.baseline)
                result['check_name'] = name
                self.results['checks'].append(result)
                
                status = result.get('status', 'unknown')
                if status == 'compliant':
                    print("✓ PASS")
                elif status == 'non-compliant':
                    print("✗ FAIL")
                else:
                    print("⚠ WARNING")
                    
            except Exception as e:
                print(f"✗ ERROR: {str(e)}")
                self.results['checks'].append({
                    'check_name': name,
                    'status': 'error',
                    'category': name,
                    'message': str(e)
                })
        
        # Calculate compliance score
        self.calculate_score()
        
        # Calculate duration
        self.results['duration'] = int(time.time() - start_time)
        
        # Save to database
        print("\n" + "-" * 60)
        print("Saving results to database...")
        scan_id = self.save_results()
        self.results['scan_id'] = scan_id
        
        # Print summary
        self.print_summary()
        
        return self.results
    
    def load_platform_modules(self, os_type):
        """Load platform-specific checking modules"""
        modules = {}
        
        try:
            if os_type == "Windows":
                from modules.windows import password_check, firewall_check
                modules = {
                    'Password Policy': password_check,
                    'Firewall': firewall_check
                }
            elif os_type == "Linux":
                from modules.linux import password_check, firewall_check
                modules = {
                    'Password Policy': password_check,
                    'Firewall': firewall_check
                }
        except ImportError as e:
            print(f"Error loading modules: {e}")
        
        return modules
    
    def calculate_score(self):
        """Calculate overall compliance score"""
        total_checks = len(self.results['checks'])
        if total_checks == 0:
            self.results['score'] = 0
            return
        
        compliant = sum(1 for c in self.results['checks'] 
                       if c.get('status') == 'compliant')
        
        self.results['score'] = round((compliant / total_checks) * 100, 2)
        self.results['total_checks'] = total_checks
        self.results['compliant_count'] = compliant
        self.results['non_compliant_count'] = total_checks - compliant
    
    def save_results(self):
        """Save scan results to database"""
        try:
            scan_id = self.db_manager.save_scan(self.results)
            return scan_id
        except Exception as e:
            print(f"Error saving to database: {e}")
            return None
    
    def print_summary(self):
        """Print scan summary"""
        print("\n" + "=" * 60)
        print("SCAN SUMMARY")
        print("=" * 60)
        print(f"Operating System: {self.results.get('os_type')}")
        print(f"Total Checks: {self.results.get('total_checks', 0)}")
        print(f"Compliant: {self.results.get('compliant_count', 0)}")
        print(f"Non-Compliant: {self.results.get('non_compliant_count', 0)}")
        print(f"Compliance Score: {self.results.get('score', 0)}%")
        print(f"Scan Duration: {self.results.get('duration', 0)} seconds")
        print("=" * 60)


if __name__ == "__main__":
    # For testing the scanner directly
    scanner = SecurityBaselineScanner()
    results = scanner.run_scan()