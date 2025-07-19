#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Voice Chatbot using OpenRouter API
Features: Text Input + Voice Output (Text-to-Speech)
"""

import json
import requests
import sys
import pyttsx3
from typing import Dict, Any

class SimpleVoiceChatbot:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the simple voice chatbot with configuration"""
        self.config = self.load_config(config_file)
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "mistralai/mistral-7b-instruct")
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        
        # Configure text-to-speech
        voices = self.engine.getProperty('voices')
        if voices:
            # Try to find a good voice
            for voice in voices:
                if "english" in voice.name.lower() or "en" in voice.id.lower():
                    self.engine.setProperty('voice', voice.id)
                    break
            else:
                self.engine.setProperty('voice', voices[0].id)
        
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
    
    def speak_text(self, text: str):
        """Convert text to speech"""
        try:
            print(f"🔊 Speaking: {text}")
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
            "X-Title": "Simple Voice Chatbot"
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
        """Start the interactive chat session with voice output"""
        print("🎤 Simple Voice Chatbot Started!")
        print("💬 Type your message and I'll speak the response")
        print("🔊 Voice commands: 'quit', 'exit', 'bye' to end")
        print("🔇 To mute voice: type 'mute' or 'text only'")
        print("🔊 To unmute: type 'unmute' or 'voice on'")
        print("=" * 50)
        
        voice_enabled = True
        
        # Initial greeting
        greeting = "Hello! I'm your voice assistant. Type your message and I'll respond with voice."
        print(f"🤖 Assistant: {greeting}")
        if voice_enabled:
            self.speak_text(greeting)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    farewell = "Goodbye! Thanks for chatting with me!"
                    print(f"\n🤖 Assistant: {farewell}")
                    if voice_enabled:
                        self.speak_text(farewell)
                    print("\n👋 Goodbye! Thanks for chatting!")
                    break
                
                # Voice control commands
                if user_input.lower() in ['mute', 'text only']:
                    voice_enabled = False
                    print("🔇 Voice disabled. Responses will be text only.")
                    continue
                
                if user_input.lower() in ['unmute', 'voice on']:
                    voice_enabled = True
                    print("🔊 Voice enabled. Responses will be spoken.")
                    continue
                
                if not user_input:
                    continue
                
                # Get response from API
                print("\n🤖 Getting response...")
                response = self.send_message(user_input)
                
                # Display and speak the response
                print(f"\n🤖 Assistant: {response}")
                if voice_enabled:
                    self.speak_text(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
    
    def test_voice_system(self):
        """Test speech synthesis"""
        print("🎤 Testing Voice System...")
        print("Testing speech synthesis...")
        
        try:
            test_text = "Hello, this is a test of the voice system."
            self.speak_text(test_text)
            print("✅ Speech synthesis working!")
            return True
        except Exception as e:
            print(f"❌ Speech synthesis error: {e}")
            return False

def main():
    """Main function to run the simple voice chatbot"""
    try:
        print("🎤 Initializing Simple Voice Chatbot...")
        chatbot = SimpleVoiceChatbot()
        
        # Test voice system first
        if chatbot.test_voice_system():
            print("\n🎤 Starting voice chat...")
            chatbot.start_chat()
        else:
            print("❌ Voice system test failed. Running in text-only mode.")
            # Still run the chat but without voice
            chatbot.start_chat()
            
    except Exception as e:
        print(f"❌ Failed to start voice chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 