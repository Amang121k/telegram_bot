# 🤖 Personal Chatbot

एक पर्सनल AI चैटबॉट जो OpenRouter API का उपयोग करके बनाया गया है। यह टर्मिनल पर text-based conversation करता है और भविष्य में voice, GUI और app integration के साथ expand किया जाएगा।

## 🚀 Features

- **Text-based Chat**: टर्मिनल पर interactive conversation
- **OpenRouter API Integration**: किसी भी supported model का उपयोग
- **Conversation Memory**: पिछले messages को याद रखता है
- **Error Handling**: Robust error handling और user-friendly messages
- **Configurable**: JSON config file से settings customize करें

## 📋 Requirements

- Python 3.7+
- `requests` library

## 🛠 Installation

1. **Dependencies Install करें:**
```bash
pip install requests
```

2. **Project Run करें:**
```bash
python3 chatbot.py
```

## ⚙️ Configuration

`config.json` file में अपनी settings customize करें:

```json
{
  "api_key": "your-openrouter-api-key",
  "model": "mistralai/mistral-7b-instruct"
}
```

### Supported Models
- `mistralai/mistral-7b-instruct`
- `openai/gpt-3.5-turbo`
- `anthropic/claude-3-sonnet`
- और भी बहुत सारे OpenRouter supported models

## 🎯 Usage

1. **Chatbot Start करें:**
```bash
python3 chatbot.py
```

2. **Message Type करें** और Enter दबाएं

3. **Exit करने के लिए** `quit`, `exit`, या `bye` type करें

## 🔮 Future Enhancements

- [ ] **Voice Input/Output**: Speech-to-text और text-to-speech
- [ ] **GUI Interface**: Tkinter या web-based interface
- [ ] **File Operations**: Files open, read, write करना
- [ ] **Web Integration**: Browser automation
- [ ] **Reminders**: Calendar और task management
- [ ] **Mobile App**: React Native या Flutter app
- [ ] **Voice Commands**: "Hey Assistant" wake word

## 🔐 Security Notes

⚠️ **Important**: 
- API key को कभी भी public repositories में share न करें
- `.gitignore` में `config.json` add करें
- Production में environment variables का उपयोग करें

## 📁 Project Structure

```
personal_chatbot/
├── chatbot.py      # Main chatbot script
├── config.json     # API configuration
└── README.md       # This file
```

## 🤝 Contributing

इस project को improve करने के लिए suggestions welcome हैं!

## 📞 Support

कोई भी issue या question हो तो contact करें।

---

**Made with ❤️ using Python and OpenRouter API** 