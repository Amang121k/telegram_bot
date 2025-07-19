#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice-Enabled Personal Chatbot using OpenRouter API
Features: Speech Recognition + Text-to-Speech
"""

import json
import requests
import sys
import speech_recognition as sr
import pyttsx3
import threading
import time
from typing import Dict, Any

class VoiceChatbot:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the voice chatbot with configuration"""
        self.config = self.load_config(config_file)
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "mistralai/mistral-7b-instruct")
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        
        # Voice settings
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        
        # Configure text-to-speech
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)  # Use first available voice
        self.engine.setProperty('rate', 150)  # Speed of speech
        self.engine.setProperty('volume', 0.9)  # Volume level
        
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
    
    def listen_for_speech(self) -> str:
        """Listen for voice input and convert to text"""
        try:
            print("🎤 Listening... (speak now)")
            
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            print("🔄 Processing speech...")
            
            # Convert speech to text
            text = self.recognizer.recognize_google(audio)
            print(f"👤 You said: {text}")
            return text
            
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            return ""
        except sr.UnknownValueError:
            print("❓ Could not understand speech")
            return ""
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return ""
        except Exception as e:
            print(f"❌ Error in speech recognition: {e}")
            return ""
    
    def speak_text(self, text: str):
        """Convert text to speech"""
        try:
            print(f"🤖 Speaking: {text}")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"❌ Error in text-to-speech: {e}")
    
    def send_message(self, message: str) -> str:
        """Send message to OpenRouter API and get response"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/personal-chatbot",
            "X-Title": "Personal Voice Chatbot"
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
    
    def start_voice_chat(self):
        """Start the interactive voice chat session"""
        print("🎤 Voice Chatbot Started!")
        print("💬 Speak your message or type 'quit' to exit")
        print("🔊 Voice commands: 'quit', 'exit', 'bye' to end")
        print("=" * 50)
        
        # Initial greeting
        greeting = "Hello! I'm your voice assistant. How can I help you today?"
        self.speak_text(greeting)
        
        while True:
            try:
                # Get input (voice or text)
                print("\n🎤 Speak or type your message:")
                user_input = input("👤 You: ").strip()
                
                # If text input is empty, try voice input
                if not user_input:
                    user_input = self.listen_for_speech()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    farewell = "Goodbye! Thanks for chatting with me!"
                    self.speak_text(farewell)
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break
                
                if not user_input:
                    continue
                
                # Get response from API
                print("\n🤖 Getting response...")
                response = self.send_message(user_input)
                
                # Speak the response
                self.speak_text(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
    
    def test_voice_system(self):
        """Test voice recognition and speech synthesis"""
        print("🎤 Testing Voice System...")
        print("1. Testing microphone...")
        
        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("✅ Microphone working!")
        except Exception as e:
            print(f"❌ Microphone error: {e}")
            return False
        
        print("2. Testing speech synthesis...")
        try:
            test_text = "Hello, this is a test of the voice system."
            self.speak_text(test_text)
            print("✅ Speech synthesis working!")
        except Exception as e:
            print(f"❌ Speech synthesis error: {e}")
            return False
        
        print("✅ Voice system test completed successfully!")
        return True

def main():
    """Main function to run the voice chatbot"""
    try:
        print("🎤 Initializing Voice Chatbot...")
        chatbot = VoiceChatbot()
        
        # Test voice system first
        if chatbot.test_voice_system():
            print("\n🎤 Starting voice chat...")
            chatbot.start_voice_chat()
        else:
            print("❌ Voice system test failed. Please check your microphone and speakers.")
            
    except Exception as e:
        print(f"❌ Failed to start voice chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 