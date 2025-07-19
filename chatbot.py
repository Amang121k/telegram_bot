#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Personal Chatbot using OpenRouter API
Author: Personal Assistant
"""

import json
import requests
import sys
from typing import Dict, Any
from langdetect import detect

# Session-wise language memory (user_id: lang)
language_memory = {}

SUPPORTED_LANGS = {
    'hi': 'हिंदी',
    'en': 'English',
    'gu': 'ગુજરાતી',
    'mr': 'मराठी',
    'ta': 'தமிழ்',
    # Add more as needed
}

# Detect language
def detect_language(text):
    try:
        lang = detect(text)
        if lang in SUPPORTED_LANGS:
            return lang
        return 'en'
    except Exception:
        return 'en'

# Build prompt with forced language
def build_prompt(user_input, detected_lang):
    if detected_lang == 'hi':
        return f"यूज़र ने कहा: {user_input}. कृपया हिंदी में जवाब दो।"
    elif detected_lang == 'gu':
        return f"વપરાશકર્તાએ કહ્યું: {user_input}. કૃપા કરીને ગુજરાતીમાં જવાબ આપો."
    elif detected_lang == 'mr':
        return f"वापरकर्त्याने म्हटले: {user_input}. कृपया मराठीत उत्तर द्या."
    elif detected_lang == 'ta':
        return f"பயனர் கூறினார்: {user_input}. தயவுசெய்து தமிழில் பதில் அளிக்கவும்."
    else:
        return f"User said: {user_input}. Please reply in English."

class PersonalChatbot:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the chatbot with configuration"""
        self.config = self.load_config(config_file)
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "mistralai/mistral-7b-instruct")
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        
        if not self.api_key:
            print("❌ Error: API key not found in config.json")
            sys.exit(1)
    
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Error: {config_file} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            print(f"❌ Error: Invalid JSON in {config_file}")
            sys.exit(1)
    
    def send_message(self, message: str) -> str:
        """Send message to OpenRouter API and get response"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/personal-chatbot",
            "X-Title": "Personal Chatbot"
        }
        
        # Prepare conversation context
        messages = []
        for msg in self.conversation_history[-10:]:  # Keep last 10 messages for context
            messages.append(msg)
        
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            return assistant_message
            
        except requests.exceptions.RequestException as e:
            return f"❌ Error connecting to API: {str(e)}"
        except KeyError as e:
            return f"❌ Error parsing API response: {str(e)}"
    
    def start_chat(self):
        """Start the interactive chat session"""
        print("🤖 Personal Chatbot Started!")
        print("💬 Type your message (type 'quit' or 'exit' to end)")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break
                
                if not user_input:
                    continue
                
                print("\n🤖 Assistant: ", end="")
                response = self.send_message(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")

def main():
    """Main function to run the chatbot"""
    try:
        chatbot = PersonalChatbot()
        chatbot.start_chat()
    except Exception as e:
        print(f"❌ Failed to start chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 