"""
Flask Backend for Doctor-Patient Translation Web App
Provides REST APIs for message translation and summarization using Google Gemini API
"""

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
import sqlite3
import os
import secrets
from datetime import datetime
import google.generativeai as genai
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables from .env if present.
load_dotenv()

# Configuration
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
DATABASE = 'db.sqlite'
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
DEMO_TOKENS = {}

# Initialize Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    model = None

# ==================== Database Setup ====================

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Check if we need to migrate old schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='conversations'")
    if cursor.fetchone():
        # Check if old schema (without doctor_id/patient_id)
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [row[1] for row in cursor.fetchall()]
        if 'doctor_id' not in columns:
            print("⚠️  Old database schema detected. Dropping tables to recreate with new schema...")
            cursor.execute('DROP TABLE IF EXISTS messages')
            cursor.execute('DROP TABLE IF EXISTS conversations')
            print("✅ Old tables dropped. Creating new schema...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('doctor', 'patient')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Conversations table (updated with doctor and patient IDs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES users (id),
            FOREIGN KEY (patient_id) REFERENCES users (id)
        )
    ''')
    
    # Messages table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER,
            sender_id INTEGER NOT NULL,
            sender_role TEXT NOT NULL,
            original_text TEXT NOT NULL,
            translated_text TEXT,
            language TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (conversation_id) REFERENCES conversations (id),
            FOREIGN KEY (sender_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully with authentication schema")

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database on startup
init_db()

# ==================== Authentication Decorators ====================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if session.get('role') != role:
                return jsonify({'error': 'Unauthorized'}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==================== Helper Functions ====================

def translate_text(text, target_language):
    """Translate text to target language using Gemini API"""
    if not model:
        return {"error": "Gemini API key not configured"}
    
    try:
        prompt = f"""Translate the following text to {target_language}. 
Only provide the translation, nothing else.

Text: {text}"""
        
        response = model.generate_content(prompt)
        return {"translated_text": response.text.strip()}
    except Exception as e:
        return {"error": str(e)}

def generate_summary(conversation_id):
    """Generate conversation summary using Gemini API"""
    if not model:
        return {"error": "Gemini API key not configured"}
    
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Fetch all messages in the conversation
        cursor.execute('''
            SELECT u.name, u.role as sender_role, m.original_text, m.translated_text, m.created_at
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = ?
            ORDER BY m.created_at ASC
        ''', (conversation_id,))
        
        messages = cursor.fetchall()
        conn.close()
        
        if not messages:
            return {"error": "No messages found"}
        
        # Build conversation text
        conversation_text = ""
        for msg in messages:
            sender = f"{msg['name']} ({msg['sender_role']})"
            original = msg['original_text']
            translated = msg['translated_text'] or original
            conversation_text += f"{sender}: {original} (Translation: {translated})\n"
        
        # Generate summary
        prompt = f"""Summarize the following doctor-patient conversation. 
Include key medical points, concerns, and recommendations.

Conversation:
{conversation_text}"""
        
        response = model.generate_content(prompt)
        return {"summary": response.text.strip()}
    except Exception as e:
        return {"error": str(e)}

def create_demo_user(role, name, email):
    """Create or fetch a demo user for the given role."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row['id']

    password_hash = generate_password_hash('demo-password-123')
    cursor.execute('''
        INSERT INTO users (name, email, password_hash, role)
        VALUES (?, ?, ?, ?)
    ''', (name, email, password_hash, role))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def ensure_demo_conversation(doctor_id, patient_id):
    """Create or fetch a demo conversation between the demo users."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id FROM conversations
        WHERE doctor_id = ? AND patient_id = ?
    ''', (doctor_id, patient_id))
    row = cursor.fetchone()
    if row:
        conn.close()
        return row['id']

    cursor.execute('''
        INSERT INTO conversations (doctor_id, patient_id)
        VALUES (?, ?)
    ''', (doctor_id, patient_id))
    conversation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return conversation_id

def login_user_by_id(user_id):
    """Load user info into session for demo login."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, role FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return False

    session['user_id'] = user['id']
    session['name'] = user['name']
    session['email'] = user['email']
    session['role'] = user['role']
    return True

# ==================== Authentication Routes ====================

@app.route('/')
def index():
    """Redirect to appropriate page based on login status"""
    if 'user_id' in session:
        if session['role'] == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        else:
            return redirect(url_for('patient_dashboard'))
    return render_template('landing.html')

@app.route('/demo')
def demo():
    """Launch demo by opening two windows for doctor and patient."""
    doctor_id = create_demo_user('doctor', 'Demo Doctor', 'demo_doctor@example.com')
    patient_id = create_demo_user('patient', 'Demo Patient', 'demo_patient@example.com')
    conversation_id = ensure_demo_conversation(doctor_id, patient_id)

    doctor_token = secrets.token_urlsafe(24)
    patient_token = secrets.token_urlsafe(24)

    DEMO_TOKENS[doctor_token] = {
        'user_id': doctor_id,
        'role': 'doctor',
        'conversation_id': conversation_id
    }
    DEMO_TOKENS[patient_token] = {
        'user_id': patient_id,
        'role': 'patient',
        'conversation_id': conversation_id
    }

    return render_template(
        'demo_launch.html',
        doctor_url=url_for('demo_doctor', token=doctor_token, _external=True),
        patient_url=url_for('demo_patient', token=patient_token, _external=True)
    )

@app.route('/demo/doctor')
def demo_doctor():
    """Auto-login demo doctor and open the conversation."""
    token = request.args.get('token', '')
    token_data = DEMO_TOKENS.get(token)
    if not token_data or token_data.get('role') != 'doctor':
        return redirect(url_for('login'))

    if not login_user_by_id(token_data['user_id']):
        return redirect(url_for('login'))

    return redirect(url_for('chat_page', conversation_id=token_data['conversation_id']))

@app.route('/demo/patient')
def demo_patient():
    """Auto-login demo patient and open the conversation."""
    token = request.args.get('token', '')
    token_data = DEMO_TOKENS.get(token)
    if not token_data or token_data.get('role') != 'patient':
        return redirect(url_for('login'))

    if not login_user_by_id(token_data['user_id']):
        return redirect(url_for('login'))

    return redirect(url_for('chat_page', conversation_id=token_data['conversation_id']))

@app.route('/register')
def register_page():
    """Serve registration page"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login')
def login():
    """Serve login page"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/doctor/dashboard')
@login_required
@role_required('doctor')
def doctor_dashboard():
    """Serve doctor dashboard"""
    return render_template('doctor_dashboard.html')

@app.route('/patient/dashboard')
@login_required
@role_required('patient')
def patient_dashboard():
    """Serve patient dashboard"""
    return render_template('patient_dashboard.html')

@app.route('/chat/<int:conversation_id>')
@login_required
def chat_page(conversation_id):
    """Serve chat page for a specific conversation"""
    return render_template('chat.html', conversation_id=conversation_id)

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

# ==================== API Routes - Authentication ====================

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.json
        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        role = data.get('role', '').lower()
        
        # Validation
        if not all([name, email, password, role]):
            return jsonify({'error': 'All fields are required'}), 400
        
        if role not in ['doctor', 'patient']:
            return jsonify({'error': 'Invalid role'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert user
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (name, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password_hash, role))
            user_id = cursor.lastrowid
            conn.commit()
            
            # Auto login
            session['user_id'] = user_id
            session['name'] = name
            session['email'] = email
            session['role'] = role
            
            conn.close()
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'role': role
            }), 201
            
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'error': 'Email already registered'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def api_login():
    """Login user"""
    try:
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not all([email, password]):
            return jsonify({'error': 'Email and password required'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user or not check_password_hash(user['password_hash'], password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Set session
        session['user_id'] = user['id']
        session['name'] = user['name']
        session['email'] = user['email']
        session['role'] = user['role']
        
        return jsonify({
            'success': True,
            'user_id': user['id'],
            'name': user['name'],
            'role': user['role']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user', methods=['GET'])
@login_required
def get_current_user():
    """Get current logged-in user info"""
    return jsonify({
        'success': True,
        'user': {
            'id': session['user_id'],
            'name': session['name'],
            'email': session['email'],
            'role': session['role']
        }
    }), 200

# ==================== API Routes - Doctors ====================

@app.route('/api/doctors', methods=['GET'])
@login_required
def get_doctors():
    """Get list of all doctors"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, name, email, created_at
            FROM users
            WHERE role = 'doctor'
            ORDER BY name ASC
        ''')
        
        doctors = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'doctors': doctors
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== API Routes - Conversations ====================

@app.route('/api/conversations', methods=['POST'])
@login_required
def create_conversation():
    """Create a new conversation between doctor and patient"""
    try:
        data = request.json
        
        if session['role'] == 'patient':
            # Patient initiates conversation with a doctor
            doctor_id = data.get('doctor_id')
            if not doctor_id:
                return jsonify({'error': 'Doctor ID required'}), 400
            patient_id = session['user_id']
        else:
            # Doctor creates conversation (would need patient_id)
            doctor_id = session['user_id']
            patient_id = data.get('patient_id')
            if not patient_id:
                return jsonify({'error': 'Patient ID required'}), 400
        
        # Check if conversation already exists
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id FROM conversations 
            WHERE doctor_id = ? AND patient_id = ?
        ''', (doctor_id, patient_id))
        
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({
                'success': True,
                'conversation_id': existing['id'],
                'existing': True
            }), 200
        
        # Create new conversation
        cursor.execute('''
            INSERT INTO conversations (doctor_id, patient_id)
            VALUES (?, ?)
        ''', (doctor_id, patient_id))
        conversation_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'existing': False
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations', methods=['GET'])
@login_required
def get_all_conversations():
    """Get all conversations for current user"""
    try:
        user_id = session['user_id']
        role = session['role']
        
        conn = get_db()
        cursor = conn.cursor()
        
        if role == 'doctor':
            # Get conversations where user is the doctor
            cursor.execute('''
                SELECT c.id, c.created_at, 
                       u.name as patient_name, u.id as patient_id,
                       COUNT(m.id) as message_count,
                       MAX(m.created_at) as last_message_at
                FROM conversations c
                JOIN users u ON c.patient_id = u.id
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.doctor_id = ?
                GROUP BY c.id
                ORDER BY last_message_at DESC, c.created_at DESC
            ''', (user_id,))
        else:
            # Get conversations where user is the patient
            cursor.execute('''
                SELECT c.id, c.created_at,
                       u.name as doctor_name, u.id as doctor_id,
                       COUNT(m.id) as message_count,
                       MAX(m.created_at) as last_message_at
                FROM conversations c
                JOIN users u ON c.doctor_id = u.id
                LEFT JOIN messages m ON c.id = m.conversation_id
                WHERE c.patient_id = ?
                GROUP BY c.id
                ORDER BY last_message_at DESC, c.created_at DESC
            ''', (user_id,))
        
        conversations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'conversations': conversations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<int:conversation_id>', methods=['GET'])
@login_required
def get_conversation_details(conversation_id):
    """Get conversation details including participants"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.created_at,
                   d.id as doctor_id, d.name as doctor_name,
                   p.id as patient_id, p.name as patient_name
            FROM conversations c
            JOIN users d ON c.doctor_id = d.id
            JOIN users p ON c.patient_id = p.id
            WHERE c.id = ?
        ''', (conversation_id,))
        
        conversation = cursor.fetchone()
        conn.close()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        # Check if user is part of this conversation
        user_id = session['user_id']
        if user_id not in [conversation['doctor_id'], conversation['patient_id']]:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'conversation': dict(conversation)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<int:conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    """Get all messages for a conversation"""
    try:
        # Verify user is part of this conversation
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT doctor_id, patient_id FROM conversations WHERE id = ?
        ''', (conversation_id,))
        
        conversation = cursor.fetchone()
        if not conversation:
            conn.close()
            return jsonify({'error': 'Conversation not found'}), 404
        
        user_id = session['user_id']
        if user_id not in [conversation['doctor_id'], conversation['patient_id']]:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403
        
        cursor.execute('''
            SELECT m.id, m.sender_id, m.sender_role, m.original_text, 
                   m.translated_text, m.language, m.created_at,
                   u.name as sender_name
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.conversation_id = ?
            ORDER BY m.created_at ASC
        ''', (conversation_id,))
        
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify({
            'success': True,
            'messages': messages
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/messages', methods=['POST'])
@login_required
def send_message():
    """Send a new message with translation"""
    try:
        data = request.json
        conversation_id = data.get('conversation_id')
        original_text = data.get('text')
        target_language = data.get('target_language', 'English')
        
        if not all([conversation_id, original_text]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Verify user is part of this conversation
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT doctor_id, patient_id FROM conversations WHERE id = ?
        ''', (conversation_id,))
        
        conversation = cursor.fetchone()
        if not conversation:
            conn.close()
            return jsonify({'error': 'Conversation not found'}), 404
        
        user_id = session['user_id']
        user_role = session['role']
        
        if user_id not in [conversation['doctor_id'], conversation['patient_id']]:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Translate the message
        translation_result = translate_text(original_text, target_language)
        
        if 'error' in translation_result:
            conn.close()
            return jsonify(translation_result), 500
        
        translated_text = translation_result['translated_text']
        
        # Store in database
        cursor.execute('''
            INSERT INTO messages (conversation_id, sender_id, sender_role, original_text, translated_text, language)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (conversation_id, user_id, user_role, original_text, translated_text, target_language))
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'original_text': original_text,
            'translated_text': translated_text
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/conversations/<int:conversation_id>/summary', methods=['GET'])
@login_required
def get_summary(conversation_id):
    """Generate and return conversation summary"""
    try:
        # Verify user is part of this conversation
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT doctor_id, patient_id FROM conversations WHERE id = ?
        ''', (conversation_id,))
        
        conversation = cursor.fetchone()
        conn.close()
        
        if not conversation:
            return jsonify({'error': 'Conversation not found'}), 404
        
        user_id = session['user_id']
        if user_id not in [conversation['doctor_id'], conversation['patient_id']]:
            return jsonify({'error': 'Unauthorized'}), 403
        
        summary_result = generate_summary(conversation_id)
        
        if 'error' in summary_result:
            return jsonify(summary_result), 500
        
        return jsonify({
            'success': True,
            'summary': summary_result['summary']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== Main ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
