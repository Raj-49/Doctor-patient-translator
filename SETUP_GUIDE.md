# 🔐 Authentication Setup Guide

## Quick Start

### 1. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 2. Set Environment Variables
```powershell
# Set your Gemini API key
$env:GEMINI_API_KEY="your-api-key-here"

# Optional: Set custom secret key for sessions
$env:SECRET_KEY="your-secret-key"
```

### 3. Run the Application
```powershell
python app.py
```

The app will be available at `http://localhost:5000`

## 🎯 User Flows

### Registration Flow
1. Navigate to `http://localhost:5000/register`
2. Fill in:
   - Full Name
   - Email Address
   - Password (min 6 characters)
   - Role: Doctor or Patient
3. Click "Create Account"
4. Automatically redirected to role-based dashboard

### Login Flow
1. Navigate to `http://localhost:5000/login`
2. Enter email and password
3. Redirected based on role:
   - **Doctors** → Doctor Dashboard
   - **Patients** → Patient Dashboard

### Doctor Workflow
1. **Dashboard**: View all patient conversations
2. **Conversations**: See list of patients who started chats
3. **Chat**: Click any conversation to open chat
4. **Messages**: Send messages with real-time translation
5. **Summary**: Generate AI-powered conversation summaries

### Patient Workflow
1. **Dashboard**: View available doctors and your conversations
2. **Start Chat**: Click any doctor to start/continue conversation
3. **Chat Interface**: 
   - Send messages to doctor
   - Messages auto-translate to target language
   - View conversation history
4. **Summary**: Generate conversation summary

## 📋 Features

✅ **User Registration** with role selection  
✅ **Secure Login** with password hashing  
✅ **Session Management** using Flask sessions  
✅ **Role-Based Dashboards** (Doctor/Patient)  
✅ **Doctor Listing** for patients  
✅ **One-to-One Conversations** (1 doctor + 1 patient)  
✅ **Real-Time Translation** via Google Gemini  
✅ **Conversation Summaries** powered by AI  
✅ **Persistent Storage** with SQLite  

## 🗄️ Database Schema

### users
- `id` - Primary key
- `name` - User's full name
- `email` - Unique email (used for login)
- `password_hash` - Hashed password
- `role` - 'doctor' or 'patient'
- `created_at` - Registration timestamp

### conversations
- `id` - Primary key
- `doctor_id` - Foreign key → users(id)
- `patient_id` - Foreign key → users(id)
- `created_at` - Conversation start time
- **Constraint**: One conversation per doctor-patient pair

### messages
- `id` - Primary key
- `conversation_id` - Foreign key → conversations(id)
- `sender_id` - Foreign key → users(id)
- `sender_role` - 'doctor' or 'patient'
- `original_text` - Original message
- `translated_text` - AI-translated text
- `language` - Target language
- `created_at` - Message timestamp

## 🔒 Security Features

- ✅ Password hashing with Werkzeug
- ✅ Flask session management
- ✅ Login required decorators
- ✅ Role-based access control
- ✅ Conversation access validation
- ✅ SQL injection prevention (parameterized queries)
- ✅ XSS prevention (HTML escaping in frontend)

## 🛠️ Testing the App

### Create Test Users

**Doctor Account:**
- Name: Dr. Smith
- Email: doctor@test.com
- Password: doctor123
- Role: Doctor

**Patient Account:**
- Name: John Patient
- Email: patient@test.com
- Password: patient123
- Role: Patient

### Test Workflow
1. Register doctor account
2. Register patient account (in different browser/incognito)
3. Patient: Click on Dr. Smith to start conversation
4. Patient: Send message in English
5. Doctor: View conversation in dashboard
6. Doctor: Reply to patient
7. Both: View translated messages
8. Either: Generate conversation summary

## 🌐 API Endpoints

### Authentication
- `POST /api/register` - Register new user
- `POST /api/login` - Login user
- `GET /api/user` - Get current user info

### Users
- `GET /api/doctors` - List all doctors (for patients)

### Conversations
- `POST /api/conversations` - Create/find conversation
- `GET /api/conversations` - List user's conversations
- `GET /api/conversations/<id>` - Get conversation details
- `GET /api/conversations/<id>/messages` - Get messages
- `GET /api/conversations/<id>/summary` - Generate summary

### Messages
- `POST /api/messages` - Send message with translation

## 📝 Notes

- **No database migrations**: Delete `db.sqlite` and restart to reset
- **Session timeout**: Sessions persist until browser close or logout
- **Auto-refresh**: Dashboards refresh every 10s, chat every 5s
- **MVP level**: Minimal error handling, suitable for demos
- **Production**: Add rate limiting, HTTPS, better validation

## 🚀 Deployment Checklist

Before production:
- [ ] Set strong `SECRET_KEY` environment variable
- [ ] Use production-grade database (PostgreSQL)
- [ ] Add HTTPS/SSL
- [ ] Implement rate limiting
- [ ] Add email verification
- [ ] Add password reset functionality
- [ ] Add input validation on backend
- [ ] Add CSRF protection
- [ ] Configure proper logging
- [ ] Set up backups

## 🆘 Troubleshooting

**"Access denied" errors:**
- Ensure you're logged in
- Check you're accessing the correct role's pages

**"Conversation not found":**
- Patient must initiate conversation first
- Check conversation_id in URL

**Database errors:**
- Delete `db.sqlite` file
- Restart application (tables recreate automatically)

**Session issues:**
- Clear browser cookies
- Set `SECRET_KEY` environment variable

---

**Built with Flask, SQLite, and Google Gemini AI**
