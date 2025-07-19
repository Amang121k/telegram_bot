#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multilingual Voice Chatbot with Human-like Behavior
Detects user's language and responds accordingly
Supports: Hindi, English, Hinglish, Marathi, Gujarati, Tamil, etc.
"""

import json
import requests
import sys
import pyttsx3
import re
import os
from typing import Dict, Any, Tuple
from gtts import gTTS
import tempfile
import platform
import subprocess

class MultilingualVoiceChatbot:
    def __init__(self, config_file: str = "config.json"):
        """Initialize the multilingual voice chatbot"""
        self.config = self.load_config(config_file)
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "mistralai/mistral-7b-instruct")
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        
        # Language detection patterns
        self.language_patterns = {
            'hindi': [
                r'[क-ह]', r'[ा-ौ]', r'[ं-ः]',  # Hindi characters
                r'\b(है|हूं|कर|दे|ले|जा|आ|गया|आया|किया|दिया)\b',
                r'\b(क्या|कैसे|कहाँ|कब|कौन|कौनसा)\b',
                r'\b(मैं|तुम|आप|हम|वह|यह|वो|ये)\b'
            ],
            'english': [
                r'\b(what|how|when|where|why|who|which)\b',
                r'\b(is|are|was|were|am|be|been|being)\b',
                r'\b(I|you|he|she|it|we|they|me|him|her|us|them)\b'
            ],
            'hinglish': [
                r'\b(ok|okay|yes|no|good|bad|nice|cool|awesome)\b',
                r'\b(thanks|thank you|please|sorry|excuse)\b',
                r'[क-ह].*[a-zA-Z]|[a-zA-Z].*[क-ह]'  # Mixed Hindi-English
            ],
            'marathi': [
                r'[क-ह]', r'[ा-ौ]', r'[ं-ः]',
                r'\b(आहे|आहोत|करतो|करते|जातो|जाते)\b',
                r'\b(मी|तू|तुम्ही|आम्ही|तो|ती|ते)\b'
            ],
            'gujarati': [
                r'[ક-હ]', r'[ા-ૌ]', r'[ં-ઃ]',
                r'\b(છે|છું|કરું|દેઉં|જાઉં|આવું)\b',
                r'\b(હું|તું|તમે|આપણે|તે|આ|એ)\b'
            ],
            'tamil': [
                r'[அ-ஹ]', r'[ா-ௌ]', r'[ஂ-ஃ]',
                r'\b(உள்ளது|உள்ளேன்|செய்கிறேன்|போகிறேன்)\b',
                r'\b(நான்|நீ|நீங்கள்|நாம்|அவன்|அவள்|அது)\b'
            ]
        }
        
        # Human-like responses for different languages
        self.human_responses = {
            'hindi': {
                'greeting': [
                    "नमस्ते! कैसे हो आप?",
                    "हैलो! क्या हाल है?",
                    "सुनो, क्या चल रहा है?",
                    "क्या हाल है भाई?"
                ],
                'thinking': [
                    "हम्म... देखते हैं",
                    "चलो सोचते हैं",
                    "अच्छा, समझ गया",
                    "ठीक है, मैं समझता हूं"
                ],
                'confused': [
                    "हम्म... यह थोड़ा मुश्किल है",
                    "समझ नहीं आ रहा",
                    "क्या मतलब है आपका?"
                ]
            },
            'english': {
                'greeting': [
                    "Hey! How are you?",
                    "Hello! What's up?",
                    "Hi there! How's it going?",
                    "What's happening?"
                ],
                'thinking': [
                    "Hmm... let me think",
                    "Well, let's see",
                    "Okay, I understand",
                    "Got it, I see what you mean"
                ],
                'confused': [
                    "Hmm... that's a bit tricky",
                    "I'm not sure I understand",
                    "What do you mean exactly?"
                ]
            },
            'hinglish': {
                'greeting': [
                    "Hey! कैसे हो?",
                    "Hello! क्या चल रहा है?",
                    "Hi! सब ठीक है?",
                    "What's up भाई?"
                ],
                'thinking': [
                    "Hmm... देखते हैं",
                    "Well, चलो सोचते हैं",
                    "Okay, समझ गया",
                    "Got it, मैं समझता हूं"
                ],
                'confused': [
                    "Hmm... यह थोड़ा tricky है",
                    "I'm not sure समझ में आ रहा",
                    "What do you mean exactly?"
                ]
            }
        }
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        self.engine.setProperty('rate', 150)
        self.engine.setProperty('volume', 0.9)
        
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
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the input text"""
        text_lower = text.lower()
        
        # Count matches for each language
        language_scores = {}
        
        for lang, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            language_scores[lang] = score
        
        # Find the language with highest score
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            if language_scores[detected_lang] > 0:
                return detected_lang
        
        # Default to English if no clear pattern
        return 'english'
    
    def get_human_response(self, language: str, response_type: str) -> str:
        """Get a human-like response based on language and type"""
        if language in self.human_responses and response_type in self.human_responses[language]:
            import random
            responses = self.human_responses[language][response_type]
            return random.choice(responses)
        return ""
    
    def speak_text(self, text: str, lang_hint: str = 'english'):
        """Smart TTS: Lekha (macOS), pyttsx3, then gTTS fallback for Hindi/Indian. Samantha for English."""
        try:
            has_hindi = bool(re.search(r'[\u0900-\u097F]', text))
            system = platform.system()
            if has_hindi:
                # 1. Try Lekha (macOS)
                if system == 'Darwin':
                    lekha_installed = subprocess.getoutput("say -v '?' | grep -i Lekha")
                    if 'Lekha' in lekha_installed:
                        os.system(f'say -v Lekha -r 180 "{text}"')
                        print(f"🔊 Speaking (Hindi, Lekha): {text}")
                        return
                # 2. Try pyttsx3 Hindi/Indian voice
                try:
                    voices = self.engine.getProperty('voices')
                    found = False
                    for voice in voices:
                        if 'hindi' in voice.name.lower() or 'indian' in voice.name.lower() or 'lekha' in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            found = True
                            break
                    self.engine.setProperty('rate', 180)
                    self.engine.say(text)
                    self.engine.runAndWait()
                    print(f"🔊 Speaking (Hindi, pyttsx3): {text}")
                    if found:
                        return
                except Exception as e:
                    print(f"⚠️ pyttsx3 Hindi voice failed: {e}")
                # 3. Try gTTS (Google TTS)
                try:
                    tts = gTTS(text=text, lang='hi')
                    with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as fp:
                        tts.save(fp.name)
                        if system == 'Darwin':
                            os.system(f'afplay "{fp.name}"')
                        elif system == 'Windows':
                            from playsound import playsound
                            playsound(fp.name)
                        else:
                            os.system(f'mpg123 "{fp.name}"')
                    print(f"🔊 Speaking (Hindi, gTTS): {text}")
                    return
                except Exception as e:
                    print(f"❌ gTTS Hindi voice failed: {e}")
                print("❌ No Hindi voice available! Please install Lekha or check internet.")
            else:
                # English/Hinglish: Samantha (macOS), else pyttsx3
                if system == 'Darwin':
                    os.system(f'say -v Samantha -r 180 "{text}"')
                    print(f"🔊 Speaking (English, Samantha): {text}")
                else:
                    try:
                        voices = self.engine.getProperty('voices')
                        for voice in voices:
                            if 'samantha' in voice.name.lower() or 'english' in voice.name.lower():
                                self.engine.setProperty('voice', voice.id)
                                break
                        self.engine.setProperty('rate', 180)
                        self.engine.say(text)
                        self.engine.runAndWait()
                        print(f"🔊 Speaking (English, pyttsx3): {text}")
                    except Exception as e:
                        print(f"❌ English TTS failed: {e}")
        except Exception as e:
            print(f"❌ Error in text-to-speech: {e}")
    
    def send_message(self, message: str, detected_language: str) -> str:
        """Send message to OpenRouter API with language context"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/personal-chatbot",
            "X-Title": "Multilingual Voice Chatbot"
        }
        
        # Create language-specific prompt
        language_prompts = {
            'hindi': "You are a helpful AI assistant. Respond in Hindi only. Be natural and conversational like a human friend. Use casual Hindi with some English words mixed in if needed.",
            'english': "You are a helpful AI assistant. Respond in English only. Be natural and conversational like a human friend.",
            'hinglish': "You are a helpful AI assistant. Respond in Hinglish (Hindi mixed with English). Be natural and conversational like a human friend. Mix Hindi and English naturally.",
            'marathi': "You are a helpful AI assistant. Respond in Marathi only. Be natural and conversational like a human friend.",
            'gujarati': "You are a helpful AI assistant. Respond in Gujarati only. Be natural and conversational like a human friend.",
            'tamil': "You are a helpful AI assistant. Respond in Tamil only. Be natural and conversational like a human friend."
        }
        
        system_prompt = language_prompts.get(detected_language, language_prompts['english'])
        
        # Prepare conversation context
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        for msg in self.conversation_history[-8:]:  # Keep last 8 messages for context
            messages.append(msg)
        
        messages.append({"role": "user", "content": message})
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,  # Slightly higher for more human-like responses
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
        """Start the interactive multilingual chat session"""
        print("🌍 Multilingual Voice Chatbot Started!")
        print("💬 Type in any language - I'll respond in the same language")
        print("🌐 Supported: Hindi, English, Hinglish, Marathi, Gujarati, Tamil")
        print("🔊 Voice commands: 'quit', 'exit', 'bye' to end")
        print("🔇 To mute voice: type 'mute' or 'text only'")
        print("🔊 To unmute: type 'unmute' or 'voice on'")
        print("=" * 60)
        
        voice_enabled = True
        current_language = 'english'
        
        # Humanized system prompt
        system_prompt = (
            "You are a friendly, witty, and natural human assistant. "
            "Always reply in the same language as the user (Hindi, English, Hinglish, Marathi, Gujarati, Tamil, etc). "
            "If the user mixes languages, you also mix naturally. "
            "Never mention you are an AI or language model. "
            "Behave like a real human friend."
        )
        
        # Initial greeting
        greeting = "Hello! I'm here to help you. You can talk to me in any language."
        print(f"🤖 Assistant: {greeting}")
        if voice_enabled:
            self.speak_text(greeting, lang_hint=current_language)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    farewell = "Goodbye! It was nice talking to you."
                    print(f"\n🤖 Assistant: {farewell}")
                    if voice_enabled:
                        self.speak_text(farewell, lang_hint=current_language)
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
                
                # Always use the same system prompt, let model handle language
                messages = [
                    {"role": "system", "content": system_prompt}
                ]
                for msg in self.conversation_history[-8:]:
                    messages.append(msg)
                messages.append({"role": "user", "content": user_input})
                data = {
                    "model": self.model,
                    "messages": messages,
                    "temperature": 0.8,
                    "max_tokens": 1000
                }
                print(f"\n🤖 Getting response...")
                try:
                    response = requests.post(
                        f"{self.base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.api_key}",
                            "Content-Type": "application/json",
                            "HTTP-Referer": "https://github.com/personal-chatbot",
                            "X-Title": "Multilingual Voice Chatbot"
                        },
                        json=data,
                        timeout=30
                    )
                    response.raise_for_status()
                    result = response.json()
                    assistant_message = result["choices"][0]["message"]["content"]
                    self.conversation_history.append({"role": "user", "content": user_input})
                    self.conversation_history.append({"role": "assistant", "content": assistant_message})
                except Exception as e:
                    assistant_message = f"❌ Error: {str(e)}"
                print(f"\n🤖 Assistant: {assistant_message}")
                if voice_enabled:
                    # Use consistent female voice for all languages
                    self.speak_text(assistant_message)
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrupted. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Unexpected error: {str(e)}")
    
    def test_voice_system(self):
        """Test speech synthesis with consistent female voice"""
        print("🎤 Testing Voice System...")
        print("Testing speech synthesis with Samantha voice...")
        
        try:
            test_text = "Hello, this is a test of the multilingual voice system."
            self.speak_text(test_text)
            print("✅ Speech synthesis working with consistent female voice!")
            return True
        except Exception as e:
            print(f"❌ Speech synthesis error: {e}")
            return False

def main():
    """Main function to run the multilingual voice chatbot"""
    try:
        print("🌍 Initializing Multilingual Voice Chatbot...")
        chatbot = MultilingualVoiceChatbot()
        
        # Test voice system first
        if chatbot.test_voice_system():
            print("\n🌍 Starting multilingual voice chat...")
            chatbot.start_chat()
        else:
            print("❌ Voice system test failed. Running in text-only mode.")
            chatbot.start_chat()
            
    except Exception as e:
        print(f"❌ Failed to start multilingual voice chatbot: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 