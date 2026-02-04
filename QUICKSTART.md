# 🚀 Quick Start Commands

Copy and paste these commands to get started quickly!

## Windows PowerShell

```powershell
# Navigate to project directory
cd "c:\OneDriveTemp\Desktop\New folder (8)"

# Install dependencies
pip install -r requirements.txt

# Set environment variables
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"

# Optional: Set custom session secret
$env:SECRET_KEY="your-custom-secret-key-for-sessions"

# Run the application
python app.py
```

## After Starting the Server

Open your browser and go to:
```
http://localhost:5000
```

## Test the Application

### Option 1: Manual Testing

**In Browser 1 (Normal mode):**
1. Go to `http://localhost:5000`
2. Click "Register here"
3. Create a doctor account:
   - Name: Dr. Smith
   - Email: doctor@test.com
   - Password: doctor123
   - Role: Doctor
4. You'll be redirected to Doctor Dashboard

**In Browser 2 (Incognito/Private mode):**
1. Go to `http://localhost:5000`
2. Click "Register here"
3. Create a patient account:
   - Name: John Patient
   - Email: patient@test.com
   - Password: patient123
   - Role: Patient
4. You'll be redirected to Patient Dashboard
5. Click on "Dr. Smith" to start a conversation
6. Send a message (e.g., "Hello doctor, I need help")
7. Set target language (e.g., "Spanish")
8. Click Send

**Back in Browser 1 (Doctor):**
1. You'll see the new conversation appear
2. Click on "John Patient"
3. View the translated message
4. Reply to the patient
5. Click "Summary" to generate AI summary

### Option 2: Automated Testing

```powershell
# Make sure the server is running first
python test_app.py
```

## Common Commands

### Check if server is running:
```powershell
# Test homepage
curl http://localhost:5000
```

### View logs in real-time:
```powershell
# Server logs appear in the terminal where you ran python app.py
```

### Reset database:
```powershell
# Stop the server (Ctrl+C)
# Delete the database
Remove-Item db.sqlite
# Restart the server
python app.py
```

### Install specific dependency:
```powershell
pip install Flask==3.0.0
pip install google-generativeai==0.3.2
pip install Werkzeug==3.0.1
```

## Troubleshooting Commands

### Check Python version:
```powershell
python --version
# Should be 3.8 or higher
```

### Check installed packages:
```powershell
pip list | Select-String -Pattern "Flask|google-generativeai|Werkzeug"
```

### Check if port 5000 is in use:
```powershell
netstat -ano | findstr :5000
```

### Kill process on port 5000 (if needed):
```powershell
# Find the PID from the netstat command above, then:
taskkill /PID <PID_NUMBER> /F
```

### Reinstall dependencies:
```powershell
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

### Check environment variables:
```powershell
$env:GEMINI_API_KEY
$env:SECRET_KEY
```

## API Testing with curl

### Register a user:
```powershell
curl -X POST http://localhost:5000/api/register `
  -H "Content-Type: application/json" `
  -d '{"name":"Test User","email":"test@example.com","password":"test123","role":"doctor"}'
```

### Login:
```powershell
curl -X POST http://localhost:5000/api/login `
  -H "Content-Type: application/json" `
  -d '{"email":"test@example.com","password":"test123"}'
```

### Get doctors list:
```powershell
curl http://localhost:5000/api/doctors
```

## Development Workflow

```powershell
# 1. Make changes to code
# 2. Server auto-reloads (debug mode)
# 3. Refresh browser to see changes

# If changes don't appear:
# - Press Ctrl+C to stop server
# - Run: python app.py
```

## Production Deployment Commands

### Set production environment variables:
```powershell
$env:SECRET_KEY="long-random-production-secret-key-change-this"
$env:GEMINI_API_KEY="your-production-api-key"
$env:FLASK_ENV="production"
```

### Run without debug mode:
Edit app.py, change last line to:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

---

## 📝 Quick Reference

| Action | Command |
|--------|---------|
| Install dependencies | `pip install -r requirements.txt` |
| Set API key | `$env:GEMINI_API_KEY="key"` |
| Run server | `python app.py` |
| Test endpoints | `python test_app.py` |
| Reset database | `Remove-Item db.sqlite` |
| Check port | `netstat -ano \| findstr :5000` |

## 🔗 Important URLs

| Page | URL |
|------|-----|
| Home/Login | http://localhost:5000 |
| Register | http://localhost:5000/register |
| Doctor Dashboard | http://localhost:5000/doctor/dashboard |
| Patient Dashboard | http://localhost:5000/patient/dashboard |
| API Docs | See SETUP_GUIDE.md |

---

**Ready to go! 🎉 Run the commands above and start using the app.**
