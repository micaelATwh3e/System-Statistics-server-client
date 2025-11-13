from flask import Flask, render_template, jsonify, request, session, redirect, url_for, flash
import sqlite3
import requests
import threading
import time
import json
from datetime import datetime, timedelta
import os
import hashlib
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this in production!

# Default admin credentials (change these!)
DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin123'

# Database setup
DB_PATH = 'stats.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create computers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS computers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            url TEXT NOT NULL,
            token TEXT NOT NULL,
            last_seen TIMESTAMP,
            status TEXT DEFAULT 'offline'
        )
    ''')
    
    # Create stats table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            computer_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cpu_percent REAL,
            memory_total INTEGER,
            memory_used INTEGER,
            memory_percent REAL,
            disk_total INTEGER,
            disk_used INTEGER,
            disk_percent REAL,
            network_bytes_sent INTEGER,
            network_bytes_recv INTEGER,
            network_sent_per_sec REAL DEFAULT 0,
            network_recv_per_sec REAL DEFAULT 0,
            FOREIGN KEY (computer_id) REFERENCES computers (id)
        )
    ''')
    
    # Add new columns for existing databases (migration)
    try:
        cursor.execute('ALTER TABLE stats ADD COLUMN network_sent_per_sec REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute('ALTER TABLE stats ADD COLUMN network_recv_per_sec REAL DEFAULT 0')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create processes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            computer_id INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pid INTEGER,
            name TEXT,
            cpu_percent REAL,
            memory_percent REAL,
            create_time REAL,
            FOREIGN KEY (computer_id) REFERENCES computers (id)
        )
    ''')
    
    # Create default admin user if no users exist
    cursor.execute('SELECT COUNT(*) FROM users')
    user_count = cursor.fetchone()[0]
    
    if user_count == 0:
        password_hash = hashlib.sha256(DEFAULT_PASSWORD.encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', (DEFAULT_USERNAME, password_hash))
        print(f"Default admin user created - Username: {DEFAULT_USERNAME}, Password: {DEFAULT_PASSWORD}")
        print("Please change the default password after first login!")
    
    conn.commit()
    conn.close()

def authenticate_user(username, password):
    """Authenticate user credentials"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute('''
        SELECT id FROM users 
        WHERE username = ? AND password_hash = ?
    ''', (username, password_hash))
    
    user = cursor.fetchone()
    conn.close()
    
    return user is not None

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session or not session['logged_in']:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def add_computer(name, url, token):
    """Add a new computer to monitor"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO computers (name, url, token, last_seen, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, url, token, datetime.now(), 'offline'))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error adding computer: {e}")
        return False
    finally:
        conn.close()

def fetch_stats_from_computer(computer_id, url, token):
    """Fetch stats from a single computer"""
    try:
        headers = {'Authorization': f'Bearer {token}'}
        response = requests.get(f"{url}/systeminfo", headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Store stats in database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get network usage rates if available
        network_sent_per_sec = data.get('network_usage', {}).get('bytes_sent_per_sec', 0)
        network_recv_per_sec = data.get('network_usage', {}).get('bytes_recv_per_sec', 0)
        
        cursor.execute('''
            INSERT INTO stats (computer_id, cpu_percent, memory_total, memory_used, 
                             memory_percent, disk_total, disk_used, disk_percent,
                             network_bytes_sent, network_bytes_recv, 
                             network_sent_per_sec, network_recv_per_sec)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            computer_id,
            data['cpu_percent'],
            data['memory']['total'],
            data['memory']['used'],
            data['memory']['percent'],
            data['disk']['total'],
            data['disk']['used'],
            data['disk']['percent'] if 'percent' in data['disk'] else (data['disk']['used'] / data['disk']['total'] * 100),
            data['network']['bytes_sent'],
            data['network']['bytes_recv'],
            network_sent_per_sec,
            network_recv_per_sec
        ))
        
        # Store process information if available
        if 'top_processes' in data and data['top_processes']:
            # Clear old processes for this computer (keep only last 1000 records)
            cursor.execute('''
                DELETE FROM processes 
                WHERE computer_id = ? AND id NOT IN (
                    SELECT id FROM processes 
                    WHERE computer_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT 1000
                )
            ''', (computer_id, computer_id))
            
            # Insert new process data
            for proc in data['top_processes']:
                cursor.execute('''
                    INSERT INTO processes (computer_id, pid, name, cpu_percent, memory_percent, create_time)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    computer_id,
                    proc.get('pid', 0),
                    proc.get('name', 'Unknown'),
                    proc.get('cpu_percent', 0),
                    proc.get('memory_percent', 0),
                    proc.get('create_time', 0)
                ))
        
        # Update computer status
        cursor.execute('''
            UPDATE computers SET last_seen = ?, status = 'online'
            WHERE id = ?
        ''', (datetime.now(), computer_id))
        
        conn.commit()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"Error fetching stats from computer {computer_id}: {e}")
        
        # Update computer status to offline
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE computers SET status = 'offline'
            WHERE id = ?
        ''', (computer_id,))
        conn.commit()
        conn.close()
        
        return False

def stats_collector():
    """Background thread to collect stats from all computers"""
    while True:
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute('SELECT id, url, token FROM computers')
            computers = cursor.fetchall()
            conn.close()
            
            for computer_id, url, token in computers:
                fetch_stats_from_computer(computer_id, url, token)
            
        except Exception as e:
            print(f"Error in stats collector: {e}")
        
        time.sleep(30)  # Collect stats every 30 seconds

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if authenticate_user(username, password):
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout and clear session"""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/computers')
@login_required
def get_computers():
    """Get list of all computers"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, name, url, last_seen, status
        FROM computers
        ORDER BY name
    ''')
    
    computers = []
    for row in cursor.fetchall():
        computers.append({
            'id': row[0],
            'name': row[1],
            'url': row[2],
            'last_seen': row[3],
            'status': row[4]
        })
    
    conn.close()
    return jsonify(computers)

@app.route('/api/stats/<int:computer_id>')
@login_required
def get_computer_stats(computer_id):
    """Get latest stats for a specific computer"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get latest stats
    cursor.execute('''
        SELECT * FROM stats
        WHERE computer_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
    ''', (computer_id,))
    
    row = cursor.fetchone()
    if row:
        stats = {
            'timestamp': row[2],
            'cpu_percent': row[3],
            'memory_total': row[4],
            'memory_used': row[5],
            'memory_percent': row[6],
            'disk_total': row[7],
            'disk_used': row[8],
            'disk_percent': row[9],
            'network_bytes_sent': row[10],
            'network_bytes_recv': row[11],
            'network_sent_per_sec': row[12] if len(row) > 12 else 0,
            'network_recv_per_sec': row[13] if len(row) > 13 else 0
        }
    else:
        stats = None
    
    conn.close()
    return jsonify(stats)

@app.route('/api/history/<int:computer_id>')
@login_required
def get_computer_history(computer_id):
    """Get historical stats for a computer"""
    hours = request.args.get('hours', 24, type=int)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT timestamp, cpu_percent, memory_percent, disk_percent
        FROM stats
        WHERE computer_id = ? AND timestamp > datetime('now', '-{} hours')
        ORDER BY timestamp
    '''.format(hours), (computer_id,))
    
    history = []
    for row in cursor.fetchall():
        history.append({
            'timestamp': row[0],
            'cpu_percent': row[1],
            'memory_percent': row[2],
            'disk_percent': row[3]
        })
    
    conn.close()
    return jsonify(history)

@app.route('/api/network_graph/<int:computer_id>')
@login_required
def get_network_graph_data(computer_id):
    """Get 24-hour network usage data for graphing"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get network usage data for the last 24 hours
    cursor.execute('''
        SELECT timestamp, network_sent_per_sec, network_recv_per_sec,
               network_bytes_sent, network_bytes_recv
        FROM stats
        WHERE computer_id = ? AND timestamp > datetime('now', '-24 hours')
        ORDER BY timestamp
    ''', (computer_id,))
    
    network_data = []
    for row in cursor.fetchall():
        network_data.append({
            'timestamp': row[0],
            'sent_per_sec': row[1] or 0,
            'recv_per_sec': row[2] or 0,
            'total_sent': row[3] or 0,
            'total_recv': row[4] or 0
        })
    
    # Get computer name for the graph title
    cursor.execute('SELECT name FROM computers WHERE id = ?', (computer_id,))
    computer_name = cursor.fetchone()
    computer_name = computer_name[0] if computer_name else 'Unknown'
    
    conn.close()
    
    return jsonify({
        'computer_name': computer_name,
        'data': network_data
    })

@app.route('/api/cpu_graph/<int:computer_id>')
@login_required
def get_cpu_graph_data(computer_id):
    """Get 24-hour CPU usage data for graphing"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get CPU usage data for the last 24 hours
    cursor.execute('''
        SELECT timestamp, cpu_percent
        FROM stats
        WHERE computer_id = ? AND timestamp > datetime('now', '-24 hours')
        ORDER BY timestamp
    ''', (computer_id,))
    
    cpu_data = []
    for row in cursor.fetchall():
        cpu_data.append({
            'timestamp': row[0],
            'cpu_percent': row[1] or 0
        })
    
    # Get computer name for the graph title
    cursor.execute('SELECT name FROM computers WHERE id = ?', (computer_id,))
    computer_name = cursor.fetchone()
    computer_name = computer_name[0] if computer_name else 'Unknown'
    
    conn.close()
    
    return jsonify({
        'computer_name': computer_name,
        'data': cpu_data
    })

@app.route('/api/processes/<int:computer_id>')
@login_required
def get_computer_processes(computer_id):
    """Get current top processes for a computer"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get the latest processes for this computer
    cursor.execute('''
        SELECT pid, name, cpu_percent, memory_percent, create_time
        FROM processes
        WHERE computer_id = ? AND timestamp > datetime('now', '-5 minutes')
        ORDER BY timestamp DESC, cpu_percent DESC
        LIMIT 20
    ''', (computer_id,))
    
    processes = []
    for row in cursor.fetchall():
        # Calculate uptime from create_time
        uptime_seconds = time.time() - row[4] if row[4] else 0
        uptime_hours = uptime_seconds / 3600
        
        processes.append({
            'pid': row[0],
            'name': row[1],
            'cpu_percent': round(row[2], 1),
            'memory_percent': round(row[3], 2),
            'uptime_hours': round(uptime_hours, 1)
        })
    
    # Get computer name
    cursor.execute('SELECT name FROM computers WHERE id = ?', (computer_id,))
    computer_name = cursor.fetchone()
    computer_name = computer_name[0] if computer_name else 'Unknown'
    
    conn.close()
    
    return jsonify({
        'computer_name': computer_name,
        'processes': processes
    })

@app.route('/api/add_computer', methods=['POST'])
@login_required
def add_computer_endpoint():
    """Add a new computer to monitor"""
    data = request.json
    name = data.get('name')
    url = data.get('url')
    token = data.get('token')
    
    if not all([name, url, token]):
        return jsonify({'error': 'Missing required fields'}), 400
    
    success = add_computer(name, url, token)
    if success:
        return jsonify({'message': 'Computer added successfully'})
    else:
        return jsonify({'error': 'Failed to add computer'}), 500

@app.route('/api/remove_computer/<int:computer_id>', methods=['DELETE'])
@login_required
def remove_computer_endpoint(computer_id):
    """Remove a computer from monitoring"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if computer exists
        cursor.execute('SELECT name FROM computers WHERE id = ?', (computer_id,))
        computer = cursor.fetchone()
        
        if not computer:
            conn.close()
            return jsonify({'error': 'Computer not found'}), 404
        
        computer_name = computer[0]
        
        # Delete related stats and processes first (foreign key constraint)
        cursor.execute('DELETE FROM stats WHERE computer_id = ?', (computer_id,))
        cursor.execute('DELETE FROM processes WHERE computer_id = ?', (computer_id,))
        
        # Delete the computer
        cursor.execute('DELETE FROM computers WHERE id = ?', (computer_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': f'Computer "{computer_name}" removed successfully'})
        
    except Exception as e:
        print(f"Error removing computer {computer_id}: {e}")
        return jsonify({'error': 'Failed to remove computer'}), 500

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change password page"""
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New passwords do not match!', 'error')
            return render_template('change_password.html')
        
        if not authenticate_user(session['username'], current_password):
            flash('Current password is incorrect!', 'error')
            return render_template('change_password.html')
        
        # Update password
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        cursor.execute('''
            UPDATE users SET password_hash = ?
            WHERE username = ?
        ''', (new_password_hash, session['username']))
        
        conn.commit()
        conn.close()
        
        flash('Password changed successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('change_password.html')

@app.route('/manage')
@login_required
def manage_computers():
    """Computer management page"""
    return render_template('manage.html')

if __name__ == '__main__':
    init_db()
    
    # Start stats collector in background thread
    collector_thread = threading.Thread(target=stats_collector, daemon=True)
    collector_thread.start()
    
    app.run(host='0.0.0.0', port=8001, debug=True)
