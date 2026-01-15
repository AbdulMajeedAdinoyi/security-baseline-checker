import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='scans.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create ScanSession table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ScanSession (
                scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date TEXT NOT NULL,
                scan_duration INTEGER,
                operating_system TEXT,
                overall_compliance_score REAL,
                total_checks INTEGER,
                compliant_count INTEGER,
                non_compliant_count INTEGER,
                warning_count INTEGER
            )
        ''')
        
        # Create CheckResult table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS CheckResult (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER,
                check_category TEXT,
                check_name TEXT,
                compliance_status TEXT,
                current_value TEXT,
                baseline_value TEXT,
                severity TEXT,
                description TEXT,
                remediation TEXT,
                FOREIGN KEY (scan_id) REFERENCES ScanSession (scan_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_scan(self, scan_data):
        """Save scan results to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Insert scan session
            cursor.execute('''
                INSERT INTO ScanSession (
                    scan_date, scan_duration, operating_system,
                    overall_compliance_score, total_checks,
                    compliant_count, non_compliant_count, warning_count
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                scan_data.get('duration', 0),
                scan_data.get('os_type', 'Unknown'),
                scan_data.get('score', 0),
                scan_data.get('total_checks', 0),
                scan_data.get('compliant_count', 0),
                scan_data.get('non_compliant_count', 0),
                scan_data.get('warning_count', 0)
            ))
            
            scan_id = cursor.lastrowid
            
            # Insert check results
            for check in scan_data.get('checks', []):
                cursor.execute('''
                    INSERT INTO CheckResult (
                        scan_id, check_category, check_name,
                        compliance_status, severity, description, remediation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    scan_id,
                    check.get('category', ''),
                    check.get('name', ''),
                    check.get('status', ''),
                    check.get('severity', ''),
                    check.get('description', ''),
                    json.dumps(check.get('remediation', ''))
                ))
            
            conn.commit()
            return scan_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_scan_history(self, limit=10):
        """Retrieve scan history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT scan_id, scan_date, operating_system, 
                   overall_compliance_score, total_checks
            FROM ScanSession
            ORDER BY scan_date DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [{
            'scan_id': r[0],
            'scan_date': r[1],
            'os': r[2],
            'score': r[3],
            'total_checks': r[4]
        } for r in results]