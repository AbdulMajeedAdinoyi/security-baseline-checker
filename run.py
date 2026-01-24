#!/usr/bin/env python
"""
Simple script to run the Flask application cleanly
"""
import os
import sys

# Set Flask environment variables
os.environ['FLASK_APP'] = 'app.py'
os.environ['FLASK_ENV'] = 'development'

# Import and run the app
from app import app

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔒 SECURITY BASELINE CHECKER - Web Server")
    print("="*70)
    print("\n✅ Server starting...")
    print("📍 Access the application at: http://127.0.0.1:5000")
    print("\nAvailable Routes:")
    print("  🏠 Dashboard:        http://127.0.0.1:5000/")
    print("  🔍 New Scan:         http://127.0.0.1:5000/scan")
    print("  📊 History:          http://127.0.0.1:5000/history")
    print("  ⚙️  Baseline Config:   http://127.0.0.1:5000/baseline")
    print("\nPress CTRL+C to stop the server")
    print("="*70 + "\n")
    
    app.run(debug=True, host='127.0.0.1', port=5000)
