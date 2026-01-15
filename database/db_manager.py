import sqlite3
import json
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path='scans.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables and apply safe migrations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create ScanSession table (with latest schema)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ScanSession (
                scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_date TEXT NOT NULL,
                scan_duration INTEGER,
                operating_system TEXT,
                detected_os TEXT,
                os_used TEXT,
                os_overridden INTEGER DEFAULT 0,
                powershell_available INTEGER DEFAULT NULL,
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

        # Safe migration: ensure new columns exist on existing DB
        cursor.execute("PRAGMA table_info('ScanSession')")
        existing_cols = {row[1] for row in cursor.fetchall()}

        needed_cols = {
            'detected_os': "ALTER TABLE ScanSession ADD COLUMN detected_os TEXT",
            'os_used': "ALTER TABLE ScanSession ADD COLUMN os_used TEXT",
            'os_overridden': "ALTER TABLE ScanSession ADD COLUMN os_overridden INTEGER DEFAULT 0",
            'powershell_available': "ALTER TABLE ScanSession ADD COLUMN powershell_available INTEGER DEFAULT NULL"
        }

        for col, alter_sql in needed_cols.items():
            if col not in existing_cols:
                try:
                    cursor.execute(alter_sql)
                except Exception as e:
                    # If column already exists due to race-conditions or concurrent migrations, ignore
                    print(f"Migration: failed to add column {col}: {e}")

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
                scan_date, scan_duration, operating_system, detected_os, os_used, os_overridden, powershell_available,
                overall_compliance_score, total_checks,
                compliant_count, non_compliant_count, warning_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
                datetime.now().isoformat(),
                scan_data.get('duration', 0),
                scan_data.get('os_type', 'Unknown'),
                scan_data.get('detected_os', None),
                scan_data.get('os_used', None),
                1 if scan_data.get('os_overridden') else 0,
                1 if scan_data.get('powershell_available') else (0 if scan_data.get('powershell_available') is False else None),
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
            SELECT scan_id, scan_date, operating_system, detected_os, os_used, os_overridden, powershell_available,
                   overall_compliance_score, total_checks
            FROM ScanSession
            ORDER BY scan_date DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        result_list = [{
            'scan_id': r[0],
            'scan_date': r[1],
            'os': r[2],
            'detected_os': r[3],
            'os_used': r[4],
            'os_overridden': bool(r[5]),
            'powershell_available': None if r[6] is None else bool(r[6]),
            'score': r[7],
            'total_checks': r[8]
        } for r in results]

        return result_list

    def get_scan_by_id(self, scan_id):
        """Retrieve a full scan result by id, including check details"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT scan_id, scan_date, operating_system, detected_os, os_used, os_overridden, powershell_available,
                   overall_compliance_score, total_checks, compliant_count, non_compliant_count, warning_count, scan_duration
            FROM ScanSession
            WHERE scan_id = ?
        ''', (scan_id,))

        row = cursor.fetchone()
        if not row:
            conn.close()
            return None

        scan = {
            'scan_id': row[0],
            'scan_date': row[1],
            'os_type': row[2],
            'detected_os': row[3],
            'os_used': row[4],
            'os_overridden': bool(row[5]),
            'powershell_available': None if row[6] is None else bool(row[6]),
            'score': row[7],
            'total_checks': row[8],
            'compliant_count': row[9],
            'non_compliant_count': row[10],
            'warning_count': row[11],
            'duration': row[12]
        }

        # Fetch associated check results
        cursor.execute('''
            SELECT check_category, check_name, compliance_status, severity, description, remediation
            FROM CheckResult
            WHERE scan_id = ?
        ''', (scan_id,))

        checks = []
        for c in cursor.fetchall():
            remediation = c[5]
            try:
                remediation = json.loads(remediation) if remediation else remediation
            except Exception:
                remediation = remediation

            checks.append({
                'category': c[0],
                'name': c[1],
                'status': c[2],
                'severity': c[3],
                'description': c[4],
                'remediation': remediation
            })

        conn.close()
        scan['checks'] = checks
        return scan

    def delete_all_scans(self):
        """Delete all scans and related check results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('DELETE FROM CheckResult')
            cursor.execute('DELETE FROM ScanSession')
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()