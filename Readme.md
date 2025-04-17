# AI Agent for Personalized GenAI Roadmaps

A powerful Flask-based web application that generates personalized GenAI learning roadmaps using Google's Gemini Pro LLM. The tool analyzes user profiles, goals, and preferences to create customized learning paths for different personas.

## ✨ Features

- 📋 **Profile Analysis**: Processes resumes (PDF, DOCX, TXT) and interview summaries
- 🎯 **Persona Classification**: Identifies user type from multiple categories
- 📊 **Multi-format Output**: Generates roadmaps in JSON, Table, and PDF formats
- 🔄 **Trace Logging**: Provides reasoning traces for roadmap decisions
- 🎨 **Modern UI**: Clean, responsive interface with gradient styling
- 📱 **Mobile-Friendly**: Adapts to different screen sizes

## 🛠️ Technology Stack

- **Backend**: Python 3.x, Flask
- **AI/ML**: Google Gemini Pro API
- **Document Processing**: 
  - PyPDF2 (PDF parsing)
  - python-docx (DOCX handling)
  - reportlab (PDF generation)
- **Frontend**: HTML5, CSS3, JavaScript
- **Environment**: python-dotenv

## 📋 Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Modern web browser
- Required Python packages (see requirements.txt)

## ⚙️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/GENAI-ROADMAP-1.git
cd GENAI-ROADMAP-1
```

2. **Create and activate virtual environment**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
# Create .env file
echo GEMINI_API_KEY=your_api_key_here > .env
echo FLASK_SECRET_KEY=your_secret_key_here >> .env
```

## 🚀 Usage

1. **Start the Flask server**
```bash
python app.py
```

2. **Access the application**
- Open your browser and navigate to `http://localhost:5000`
- Upload your resume or paste resume text
- Add interview summary
- Specify your learning goals
- Click "Generate Roadmap"

## 📁 Project Structure

```
GENAI-ROADMAP-1/
├── app.py                 # Main Flask application
├── roadmap_agent.py       # Core roadmap generation logic
├── file_text_utils.py     # File processing utilities
├── requirements.txt       # Project dependencies
├── templates/
│   └── index.html        # Main web interface
└── .env                  # Environment variables
```

## 🔧 Configuration

Key configurations are managed through environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `FLASK_SECRET_KEY`: Secret key for Flask session management

## 🎯 Supported User Personas

- College student
- Working professional (tech)
- Working professional (non-tech)
- Marketing/Sales background
- Non-tech aiming to enter tech
- Senior professional (10+ years experience)

## 📤 Output Formats

1. **JSON**: Structured roadmap data
2. **Table**: Human-readable formatted text
3. **PDF**: Professional document with proper formatting (requires reportlab)

## 🎥 Demo

Check out our demo video to see GENAI-ROADMAP-1 in action:

[![GENAI-ROADMAP-1 Demo](https://img.youtube.com/vi/YOUR_VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=YOUR_VIDEO_ID)

> 🎯 The demo shows:
> - Resume upload and analysis
> - Persona classification
> - Roadmap generation
> - Different output formats
> - User interface walkthrough

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- Flask framework and its community
- All open-source libraries used in this project

---
⭐ Star me on GitHub — it helps!