from flask import Flask, render_template, jsonify, request, session, redirect, url_for
import sqlite3
from datetime import datetime, timedelta
import json
from functools import wraps

app = Flask(__name__)
app.secret_key = 'costbyte_dashboard_secret_2024'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('data/costbyte.db')
    conn.row_factory = sqlite3.Row
    return conn

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/api/dashboard-data')
@login_required
def dashboard_data():
    conn = get_db_connection()
    
    # Revenue data
    revenue_data = get_revenue_data(conn)
    
    # Client data
    client_data = get_client_data(conn)
    
    # System health data
    system_data = get_system_data(conn)
    
    conn.close()
    
    return jsonify({
        'revenue': revenue_data,
        'clients': client_data,
        'system': system_data,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/client-details')
@login_required
def client_details():
    conn = get_db_connection()
    
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            c.id,
            c.company_name,
            c.contact_person,
            c.email,
            c.location,
            c.country,
            crs.total_revenue,
            crs.first_payment,
            crs.last_payment,
            (SELECT service_tier FROM client_payments WHERE client_id = c.id ORDER BY payment_date DESC LIMIT 1) as current_tier
        FROM clients c
        LEFT JOIN client_revenue_summary crs ON c.id = crs.client_id
        WHERE c.status = 'active'
        ORDER BY crs.total_revenue DESC
    ''')
    
    clients = []
    for row in cursor.fetchall():
        clients.append({
            'id': row['id'],
            'company_name': row['company_name'],
            'contact_person': row['contact_person'],
            'email': row['email'],
            'location': row['location'],
            'country': row['country'],
            'total_revenue': row['total_revenue'] or 0,
            'first_payment': row['first_payment'],
            'last_payment': row['last_payment'],
            'current_tier': row['current_tier'] or 'professional'
        })
    
    conn.close()
    return jsonify(clients)

@app.route('/api/revenue-growth')
@login_required
def revenue_growth():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            strftime('%Y-%m', payment_date) as month,
            SUM(amount) as revenue,
            COUNT(DISTINCT client_id) as clients
        FROM client_payments 
        WHERE payment_date >= date('now', '-12 months')
        GROUP BY strftime('%Y-%m', payment_date)
        ORDER BY month
    ''')
    
    growth_data = []
    for row in cursor.fetchall():
        growth_data.append({
            'month': row['month'],
            'revenue': row['revenue'],
            'clients': row['clients']
        })
    
    conn.close()
    return jsonify(growth_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication - in production, use proper auth
        if username == 'admin' and password == 'costbyte2024':
            session['user_id'] = 1
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

def get_revenue_data(conn):
    cursor = conn.cursor()
    
    # Current month revenue
    cursor.execute('''
        SELECT SUM(amount) as revenue FROM client_payments 
        WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
    ''')
    current_revenue = cursor.fetchone()['revenue'] or 0
    
    # Target progress
    target_revenue = 1000000
    progress = (current_revenue / target_revenue) * 100
    
    # Monthly growth
    cursor.execute('''
        SELECT 
            strftime('%Y-%m', payment_date) as month,
            SUM(amount) as revenue
        FROM client_payments 
        WHERE payment_date >= date('now', '-6 months')
        GROUP BY strftime('%Y-%m', payment_date)
        ORDER BY month DESC
        LIMIT 6
    ''')
    
    monthly_data = []
    for row in cursor.fetchall():
        monthly_data.append({
            'month': row['month'],
            'revenue': row['revenue']
        })
    
    return {
        'current_revenue': current_revenue,
        'target_revenue': target_revenue,
        'progress_percentage': round(progress, 1),
        'monthly_trend': monthly_data[::-1]  # Reverse to show chronological order
    }

def get_client_data(conn):
    cursor = conn.cursor()
    
    # Active clients
    cursor.execute('''
        SELECT COUNT(DISTINCT client_id) as count FROM client_payments 
        WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
    ''')
    active_clients = cursor.fetchone()['count'] or 0
    
    # Client tiers
    cursor.execute('''
        SELECT service_tier, COUNT(*) as count 
        FROM client_payments 
        WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
        GROUP BY service_tier
    ''')
    
    tiers = {}
    for row in cursor.fetchall():
        tiers[row['service_tier']] = row['count']
    
    # Top clients
    cursor.execute('''
        SELECT 
            c.company_name,
            SUM(cp.amount) as total_revenue
        FROM client_payments cp
        JOIN clients c ON cp.client_id = c.id
        WHERE strftime('%Y-%m', cp.payment_date) = strftime('%Y-%m', 'now')
        GROUP BY c.company_name
        ORDER BY total_revenue DESC
        LIMIT 5
    ''')
    
    top_clients = []
    for row in cursor.fetchall():
        top_clients.append({
            'company_name': row['company_name'],
            'revenue': row['total_revenue']
        })
    
    return {
        'active_clients': active_clients,
        'tier_distribution': tiers,
        'top_clients': top_clients
    }

def get_system_data(conn):
    # This would integrate with the actual system monitoring
    return {
        'status': 'healthy',
        'uptime': '99.9%',
        'last_updated': datetime.now().isoformat()
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
