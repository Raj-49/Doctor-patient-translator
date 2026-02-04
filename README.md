# 🏥 Doctor-Patient Translation Web App

A production-ready Flask web application that enables real-time translation and summarization of doctor-patient conversations using Google Gemini AI.

## 🌟 Features

- **Real-time Translation**: Automatically translate messages between doctor and patient in any language
- **AI-Powered Summaries**: Generate comprehensive conversation summaries using Google Gemini
- **Conversation Management**: Create and manage multiple conversation sessions
- **Persistent Storage**: SQLite database for storing all conversations and messages
- **Clean UI**: Modern, responsive interface built with vanilla JavaScript
- **REST API**: Well-structured RESTful endpoints for easy integration
- **No Authentication**: Simple, open access (suitable for demos and internal use)

## 📁 Project Structure

```
project/
├── app.py                 # Flask backend with REST APIs
├── db.sqlite             # SQLite database (auto-created)
├── templates/
│   └── index.html        # Frontend HTML
├── static/
│   ├── style.css         # Styling
│   └── script.js         # Frontend JavaScript
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone or download this project**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up your Google Gemini API key**

   **Windows (PowerShell):**
   ```powershell
   $env:GEMINI_API_KEY="your-api-key-here"
   ```

   **Windows (Command Prompt):**
   ```cmd
   set GEMINI_API_KEY=your-api-key-here
   ```

   **Linux/Mac:**
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

   *For permanent setup, create a `.env` file:*
   ```
   GEMINI_API_KEY=your-api-key-here
   ```

4. **Run the application**
```bash
python app.py
```

5. **Open your browser**
   Navigate to: `http://localhost:5000`

## 🎯 Usage

### Creating a Conversation

1. Click **"➕ New Conversation"** to start a new session
2. The conversation will be activated automatically

### Sending Messages

1. Select the sender type (👨‍⚕️ Doctor or 🧑 Patient)
2. Enter the target language for translation (e.g., "Spanish", "French", "Mandarin")
3. Type your message in the text area
4. Click **"Send ➤"** or press Enter

### Generating Summaries

1. Ensure you have an active conversation with messages
2. Click **"📋 Generate Summary"**
3. View the AI-generated summary of the entire conversation

### Managing Conversations

- Use the dropdown to switch between different conversations
- All conversations are automatically saved
- Message counts are displayed for each conversation

## 🔌 REST API Endpoints

### Conversations

- **POST** `/api/conversations` - Create a new conversation
- **GET** `/api/conversations` - Get all conversations
- **GET** `/api/conversations/<id>/messages` - Get messages for a conversation
- **GET** `/api/conversations/<id>/summary` - Generate conversation summary

### Messages

- **POST** `/api/messages` - Send a new message with translation
  ```json
  {
    "conversation_id": 1,
    "sender": "doctor",
    "text": "How are you feeling today?",
    "target_language": "Spanish"
  }
  ```

## 🗄️ Database Schema

### conversations
| Column     | Type      | Description                    |
|------------|-----------|--------------------------------|
| id         | INTEGER   | Primary key                    |
| created_at | TIMESTAMP | Conversation creation time     |

### messages
| Column          | Type      | Description                    |
|-----------------|-----------|--------------------------------|
| id              | INTEGER   | Primary key                    |
| conversation_id | INTEGER   | Foreign key to conversations   |
| sender          | TEXT      | "doctor" or "patient"          |
| original_text   | TEXT      | Original message               |
| translated_text | TEXT      | AI-translated message          |
| language        | TEXT      | Target translation language    |
| created_at      | TIMESTAMP | Message creation time          |

## ⚙️ Configuration

### Environment Variables

- `GEMINI_API_KEY` - Your Google Gemini API key (required)

### Flask Settings

Modify these in `app.py` if needed:
- `DEBUG` - Development mode (default: True)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 5000)

## 🛠️ Technology Stack

### Backend
- **Flask 3.0.0** - Lightweight Python web framework
- **SQLite3** - Built-in database (no separate installation needed)
- **Google Gemini API** - AI for translation and summarization

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS Grid and Flexbox
- **Vanilla JavaScript** - No frameworks, pure ES6+

## 🔒 Security Considerations

⚠️ **Important**: This application has no authentication system and is designed for:
- Development and testing
- Internal/private networks
- Demonstration purposes

For production deployment:
- Implement user authentication
- Add rate limiting
- Use HTTPS
- Validate and sanitize all inputs
- Store API keys securely (not in environment variables)
- Add CORS protection
- Implement proper error handling and logging

## 🐛 Troubleshooting

### "Gemini API key not configured"
- Ensure the `GEMINI_API_KEY` environment variable is set
- Restart the Flask server after setting the variable

### Database errors
- Delete `db.sqlite` and restart the app to recreate tables
- Check file permissions in the project directory

### API errors
- Verify your Gemini API key is valid
- Check your internet connection
- Review the Flask console for detailed error messages

## 📝 License

This project is provided as-is for educational and demonstration purposes.

## 🤝 Contributing

This is a minimal demonstration project. Feel free to fork and modify for your needs.

## 📧 Support

For issues related to:
- **Flask**: https://flask.palletsprojects.com/
- **Google Gemini API**: https://ai.google.dev/docs

---

**Built with ❤️ using Flask and Google Gemini AI**
