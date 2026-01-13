# 🤖 AI Chatbot with Long Term Memory

An intelligent conversational AI chatbot powered by Google Gemini with persistent long-term memory, user profiles, and customizable conversation tones. The application maintains context across sessions and adapts responses based on user preferences.

## ✨ Features

- **🧠 Long-Term Memory**: Chatbot remembers previous conversations and maintains context across sessions
- **👥 Multi-User Support**: Create and manage multiple user profiles with different conversation tones
- **🎭 Customizable Tones**: Choose from multiple conversation styles (Technical, Friendly, Casual)
- **💾 Persistent Storage**: Conversations and user data are stored locally in JSON format
- **🎨 Modern UI**: Beautiful, responsive interface with smooth animations and gradient designs
- **⚡ Real-Time Processing**: Instant message processing with thinking indicators
- **🔐 Data Isolation**: Each user's data is completely isolated and secure
- **📊 Session Statistics**: View conversation statistics and memory usage per user

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Google Gemini API key

### ⚡ Quick Setup (Windows - Recommended)

**For first-time setup only:**
```bash
setup.bat
```

This script will:
- ✅ Create a virtual environment
- ✅ Install all dependencies from requirements.txt
- ✅ Guide you to set up your API key
- ✅ Show you how to run the app

**To run the app after setup:**
```bash
run.bat
```

This script will activate the virtual environment and start the Streamlit app.

---

### 📋 Manual Setup (Cross-Platform)

If you prefer manual setup or are on macOS/Linux:

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-chatbot-memory.git
   cd ai-chatbot-memory
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv genai_env
   
   # On Windows
   genai_env\Scripts\activate
   
   # On macOS/Linux
   source genai_env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```
   
   Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

5. **Run the application**
   ```bash
   # On Windows
   streamlit run app/streamlit_app.py
   
   # On macOS/Linux
   python -m streamlit run app/streamlit_app.py
   ```

The application will open in your browser at `http://localhost:8501`

---

### 📝 Setup File Information

| File | Purpose | When to Use |
|------|---------|-----------|
| **setup.bat** | First-time setup (creates env, installs packages, sets API key) | Run **once** after cloning |
| **run.bat** | Quick startup after initial setup | Run every time you want to use the app |

⚠️ **Important**: Run `setup.bat` only on your first time. It will error if the virtual environment already exists.

## 📖 Usage Guide

### Starting a Conversation

1. **Select or Create a User Profile**
   - Choose an existing user from the sidebar
   - Or create a new profile with your name and preferred conversation tone

2. **Choose Your Tone**
   - **Technical**: For detailed, technical discussions with code examples
   - **Friendly**: For warm, conversational interactions
   - **Casual**: For relaxed, informal chats

3. **Type Your Message**
   - Enter your message in the input box
   - Click the send button (➤) or press Enter
   - The chatbot will respond while maintaining conversation context

### Managing Your Profile

- **Edit Profile**: Update your display name or conversation tone
- **Clear Chat**: Remove current session messages (keeps long-term memory)
- **View Memory**: Browse your stored conversation history
- **Delete Profile**: Permanently remove your profile and data

## 🏗️ Project Structure

```
ai-chatbot-memory/
├── app/
│   └── streamlit_app.py          # Main Streamlit application
├── memory/
│   └── memory_store.py           # Long-term memory management
├── retrieval/
│   └── context_retriever.py      # Context retrieval and processing
├── generation/
│   └── response_generator.py     # AI response generation
├── profiles/
│   └── user_profile.py           # User profile management
├── conversation_history.json     # Stored conversations (auto-generated)
├── user_profiles.json            # User profiles (auto-generated)
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (create locally)
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## 📦 Dependencies

- **streamlit**: Web application framework for creating interactive applications
- **google-genai**: Google Gemini AI API client for accessing the language model
- **torch**: Deep learning framework for ML operations
- **sentence-transformers**: For semantic text encoding and similarity
- **transformers**: NLP transformers library for text processing
- **python-dotenv**: Environment variable management

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root with:

```env
GEMINI_API_KEY=your_api_key_here
```

### AI Model Configuration

**Tested Models**: This chatbot has been tested with:
- **Gemini 2.5 Flash** (Primary model - recommended)
- **Gemini 2.5 Flash Lite** (Lightweight alternative)

You can use any Gemini model that your API supports. To change the model:

1. Open [generation/response_generator.py](generation/response_generator.py)
2. Find the line that specifies the model (around line 185):
   ```python
   response = client.models.generate_content(
       model="gemini-2.5-flash",  # ← Change this line
       contents=prompt,
       config={...}
   )
   ```
3. Replace `"gemini-2.5-flash"` with your desired model:
   - `"gemini-2.5-flash-lite"` for the lightweight version
   - `"gemini-1.5-pro"` for other available models
   - Or any other supported Gemini model

**Note**: Ensure your API key has access to the model you select.

### Customizing Tone Instructions

Edit [generation/response_generator.py](generation/response_generator.py) to customize AI responses:

- Modify tone-specific system prompts
- Add new conversation styles
- Adjust response behavior and personality

## 💾 Data Storage

The application stores data locally in JSON format:

- **conversation_history.json**: All messages and bot responses with timestamps
- **user_profiles.json**: User information (ID, display name, tone preference)

These files are created automatically on first run and stored in the project root directory.

## 🔐 Security & Privacy

- ✅ **Local Storage**: All data stored locally - no cloud uploads
- ✅ **Data Isolation**: Each user's data is completely isolated
- ✅ **Secure Credentials**: API keys stored in `.env` (never committed to git)
- ✅ **Git Protection**: `.gitignore` prevents accidental credential leaks
- ✅ **No Tracking**: No analytics or user tracking

## 🎯 How It Works

### Memory System Architecture

The chatbot uses a three-layer memory approach:

1. **Session Memory**: Current conversation messages displayed in chat UI
2. **Long-Term Memory**: All previous conversations stored in `conversation_history.json`
3. **Context Retrieval**: Most relevant past messages retrieved for current response

### Conversation Flow

```
User Input
    ↓
Load User Profile & Tone Preference
    ↓
Retrieve Complete Conversation History
    ↓
Generate Context from Past Messages
    ↓
Call Gemini API with Full Context
    ↓
Store Response in Long-Term Memory
    ↓
Display in Chat UI with Animations
```

## 🎨 UI Features

- **Gradient Message Bubbles**: 
  - User messages: Purple/indigo gradient
  - Bot messages: Cyan/teal gradient
  - High contrast with white text for readability

- **Smooth Animations**:
  - Slide-in effects for messages
  - Bounce animations for thinking indicator
  - Hover scale effects on messages

- **Responsive Design**: 
  - Works seamlessly on desktop and mobile
  - Adaptive layout for different screen sizes

- **Dark Theme**: 
  - Modern dark interface (easy on the eyes)
  - Glassmorphism effects in sidebar
  - Custom scrollbar styling

## 🚀 Deployment

### Option 1: Streamlit Cloud (Recommended)

1. Push code to GitHub (ensure `.env` and data files are in `.gitignore`)
2. Go to [Streamlit Cloud](https://share.streamlit.io/)
3. Deploy from your GitHub repository
4. Add `GEMINI_API_KEY` to Secrets in the Streamlit Cloud dashboard

### Option 2: Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "app/streamlit_app.py"]
```

Build and run:
```bash
docker build -t ai-chatbot .
docker run -e GEMINI_API_KEY=your_key -p 8501:8501 ai-chatbot
```

### Option 3: Traditional Server

1. Install Python and dependencies
2. Run with a production WSGI server
3. Use a reverse proxy (nginx/Apache)
4. Set environment variables on server

## 🐛 Troubleshooting

### Issue: "API key not found"
**Solution:**
- Ensure `.env` file exists in project root
- Verify `GEMINI_API_KEY=your_actual_key` (no spaces or quotes)
- Restart the Streamlit app: `Ctrl+C` then run again

### Issue: "No messages display"
**Solution:**
- Check that `conversation_history.json` exists
- Clear browser cache and refresh page
- Try creating a new user profile
- Check browser console for errors (F12)

### Issue: Slow responses
**Solution:**
- Verify internet connection
- Check API rate limits in Google Cloud console
- Ensure Gemini API is enabled in your Google account
- Try with a simpler message

### Issue: Module import errors
**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify virtual environment is activated
# On Windows: genai_env\Scripts\activate
# On macOS/Linux: source genai_env/bin/activate
```

## 📝 License

This project is open source and available under the MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and commit (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📞 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub Issues
- Check existing issues for solutions
- Review the troubleshooting section above

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/) - for the amazing web framework
- Powered by [Google Gemini AI](https://ai.google.dev/) - for the language model
- Community for feedback and suggestions

## 🎓 Learn More

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Google Gemini API Docs](https://ai.google.dev/docs)
- [Python Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [Git & GitHub Basics](https://guides.github.com/)

## 🎯 Roadmap

Future enhancements planned:
- [ ] Speech-to-text input
- [ ] Export conversation as PDF
- [ ] Dark/Light theme toggle
- [ ] User authentication
- [ ] Cloud storage option
- [ ] Multi-language support

---

**Built with ❤️ for intelligent conversations with memory** | Last Updated: January 2026
