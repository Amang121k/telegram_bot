#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Stylish, Funny, Pastel Light-Mode GUI Chatbot
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import requests
import sys
import pyttsx3
import os
import platform
import subprocess
import tempfile
import re
from gtts import gTTS
from typing import Dict, Any
import random

# Optional voice recognition import
try:
    import speech_recognition as sr
    VOICE_RECOGNITION_AVAILABLE = True
except ImportError:
    VOICE_RECOGNITION_AVAILABLE = False
    print("⚠️ Voice recognition not available (PyAudio not installed)")
    print("💡 Install with: pip install PyAudio")
    print("📝 Voice input will be disabled, but text input and voice output will work")

# Pastel color palette
PASTEL_USER = '#b2f7ef'
PASTEL_BOT = '#f7d6e0'
PASTEL_BG = '#f9f9f9'
PASTEL_HEADER = '#ffe5b4'
PASTEL_FOOTER = '#e0e7ff'
PASTEL_ACCENT = '#ffd6e0'
FONT_MAIN = ('Comic Sans MS', 12)
FONT_HEADER = ('Comic Sans MS', 16, 'bold')
FONT_BUBBLE = ('Comic Sans MS', 12)

BOT_EMOJIS = ['😎', '🤖', '😂', '🙃', '🥳', '😜', '✨', '😏', '😇', '🤩', '😺', '🦄', '🍕', '🥒', '🎉']
BOT_WITTY = [
    "Did you know? I run on pure coffee ☕️!",
    "I'm 99% code, 1% bad puns.",
    "If I had hands, I'd high-five you! 🙌",
    "My favorite color is... #00FF00!",
    "I dream in Python 🐍.",
    "Sometimes I pretend to be a toaster. 🍞",
    "I never sleep, but I do daydream!",
    "Ask me anything, except my browser history. 😅",
    "I love talking to you!"
]

class StylishChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Personal AI Assistant ✨")
        self.root.geometry("850x650")
        self.root.configure(bg=PASTEL_BG)
        
        # Load configuration
        self.config = self.load_config("config.json")
        self.api_key = self.config.get("api_key")
        self.model = self.config.get("model", "mistralai/mistral-7b-instruct")
        self.base_url = "https://openrouter.ai/api/v1"
        self.conversation_history = []
        
        # Voice settings
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 180)
        self.engine.setProperty('volume', 0.9)
        
        # Voice recognition setup (optional)
        if VOICE_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                self.voice_input_available = True
            except Exception as e:
                print(f"⚠️ Voice recognition setup failed: {e}")
                self.voice_input_available = False
        else:
            self.voice_input_available = False
        
        # GUI state
        self.voice_enabled = tk.BooleanVar(value=True)
        self.is_listening = False
        
        self.setup_gui()
        
    def load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            messagebox.showerror("Error", f"{config_file} not found")
            sys.exit(1)
        except json.JSONDecodeError:
            messagebox.showerror("Error", f"Invalid JSON in {config_file}")
            sys.exit(1)
    
    def setup_gui(self):
        """Setup the GUI layout"""
        # Header
        header = tk.Label(self.root, text="🤖 Personal AI Assistant ✨", bg=PASTEL_HEADER, fg="#333", font=FONT_HEADER, pady=10)
        header.pack(fill=tk.X)
        
        # Funny bot mood
        self.mood_var = tk.StringVar()
        self.set_random_mood()
        mood_label = tk.Label(self.root, textvariable=self.mood_var, bg=PASTEL_HEADER, fg="#666", font=('Comic Sans MS', 11, 'italic'))
        mood_label.pack(fill=tk.X)
        
        # Chat area frame
        chat_frame = tk.Frame(self.root, bg=PASTEL_BG)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(10, 0))
        
        # Canvas for chat bubbles
        self.chat_canvas = tk.Canvas(chat_frame, bg=PASTEL_BG, highlightthickness=0)
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=self.chat_canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Frame inside canvas
        self.bubble_frame = tk.Frame(self.chat_canvas, bg=PASTEL_BG)
        self.chat_canvas.create_window((0, 0), window=self.bubble_frame, anchor='nw')
        self.bubble_frame.bind("<Configure>", lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all")))
        
        # Input area
        input_frame = tk.Frame(self.root, bg=PASTEL_BG)
        input_frame.pack(fill=tk.X, pady=(10, 0), padx=20)
        
        # Text input
        self.text_input = tk.Entry(input_frame, font=FONT_MAIN, bg="#fff", fg="#333", relief=tk.GROOVE, bd=2)
        self.text_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5), ipady=6)
        self.text_input.bind('<Return>', self.send_message)
        
        # Voice input button
        if self.voice_input_available:
            self.voice_button = tk.Button(input_frame, text="🎤", font=FONT_MAIN, bg=PASTEL_ACCENT, relief=tk.FLAT, command=self.toggle_voice_input, width=3, activebackground="#fff")
            self.voice_button.pack(side=tk.LEFT, padx=(0, 5))
        else:
            self.voice_button = tk.Button(input_frame, text="🎤", font=FONT_MAIN, bg=PASTEL_ACCENT, relief=tk.FLAT, state='disabled', width=3)
            self.voice_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Send button
        send_button = tk.Button(input_frame, text="Send 🚀", font=FONT_MAIN, bg=PASTEL_USER, relief=tk.RAISED, command=self.send_message, activebackground=PASTEL_BOT)
        send_button.pack(side=tk.LEFT)
        
        # Control buttons frame
        control_frame = tk.Frame(self.root, bg=PASTEL_BG)
        control_frame.pack(fill=tk.X, padx=20, pady=(5, 0))
        
        # Voice toggle
        voice_check = tk.Checkbutton(control_frame, text="🔊 Voice Output", variable=self.voice_enabled, font=('Comic Sans MS', 11), bg=PASTEL_BG, activebackground=PASTEL_BG)
        voice_check.pack(side=tk.LEFT)
        
        # Clear chat button
        clear_button = tk.Button(control_frame, text="🧹 Clear Chat", font=('Comic Sans MS', 11), bg=PASTEL_ACCENT, relief=tk.RAISED, command=self.clear_chat)
        clear_button.pack(side=tk.RIGHT)
        
        # Footer
        footer = tk.Label(self.root, text="Made with ❤️ and bad puns by your AI buddy!", bg=PASTEL_FOOTER, fg="#555", font=('Comic Sans MS', 10, 'italic'), pady=8)
        footer.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Initial greeting
        self.add_message("🤖 Assistant", "Hello! I'm your personal AI assistant. How can I help you today? " + random.choice(BOT_EMOJIS))
        if not self.voice_input_available:
            self.add_message("ℹ️ System", "Voice input is disabled. Install PyAudio for voice input: pip install PyAudio")
    
    def set_random_mood(self):
        mood = random.choice(BOT_WITTY)
        emoji = random.choice(BOT_EMOJIS)
        self.mood_var.set(f"Bot Mood: {mood} {emoji}")
    
    def add_message(self, sender: str, message: str):
        """Add message to chat display"""
        # Chat bubble style
        is_user = sender.startswith("👤")
        bubble_color = PASTEL_USER if is_user else PASTEL_BOT
        anchor = 'e' if is_user else 'w'
        padx = (60, 10) if is_user else (10, 60)
        
        # Frame for bubble
        bubble = tk.Frame(self.bubble_frame, bg=PASTEL_BG)
        bubble.pack(anchor=anchor, pady=4, padx=padx, fill=tk.X, expand=True)
        
        # Bubble label
        bubble_label = tk.Label(
            bubble,
            text=message,
            font=FONT_BUBBLE,
            bg=bubble_color,
            fg="#333",
            wraplength=500,
            justify=tk.LEFT if not is_user else tk.RIGHT,
            bd=0,
            padx=12,
            pady=8,
            relief=tk.FLAT,
            anchor=anchor
        )
        bubble_label.pack(side=tk.RIGHT if is_user else tk.LEFT, fill=tk.NONE, expand=False)
        
        # Sender label (small)
        sender_label = tk.Label(
            bubble,
            text=sender,
            font=('Comic Sans MS', 9, 'italic'),
            bg=PASTEL_BG,
            fg="#888"
        )
        sender_label.pack(side=tk.RIGHT if is_user else tk.LEFT, anchor=anchor)
        
        # Scroll to bottom
        self.root.after(100, lambda: self.chat_canvas.yview_moveto(1.0))
    
    def speak_text(self, text: str):
        """Smart TTS with fallback"""
        if not self.voice_enabled.get():
            return
            
        try:
            has_hindi = bool(re.search(r'[\u0900-\u097F]', text))
            system = platform.system()
            
            if has_hindi:
                # Try Lekha (macOS)
                if system == 'Darwin':
                    lekha_installed = subprocess.getoutput("say -v '?' | grep -i Lekha")
                    if 'Lekha' in lekha_installed:
                        os.system(f'say -v Lekha -r 180 "{text}"')
                        return
                
                # Try pyttsx3 Hindi voice
                try:
                    voices = self.engine.getProperty('voices')
                    for voice in voices:
                        if 'hindi' in voice.name.lower() or 'indian' in voice.name.lower():
                            self.engine.setProperty('voice', voice.id)
                            break
                    self.engine.say(text)
                    self.engine.runAndWait()
                    return
                except Exception:
                    pass
                
                # Try gTTS
                try:
                    tts = gTTS(text=text, lang='hi')
                    with tempfile.NamedTemporaryFile(delete=True, suffix='.mp3') as fp:
                        tts.save(fp.name)
                        if system == 'Darwin':
                            os.system(f'afplay "{fp.name}"')
                        else:
                            os.system(f'mpg123 "{fp.name}"')
                    return
                except Exception:
                    pass
            else:
                # English: Samantha (macOS) or pyttsx3
                if system == 'Darwin':
                    os.system(f'say -v Samantha -r 180 "{text}"')
                else:
                    self.engine.say(text)
                    self.engine.runAndWait()
                    
        except Exception as e:
            print(f"Voice error: {e}")
    
    def send_message(self, event=None):
        """Send message to API and get response"""
        message = self.text_input.get().strip()
        if not message:
            return
        
        # Clear input
        self.text_input.delete(0, tk.END)
        
        # Add user message
        self.add_message("👤 You", message)
        self.set_random_mood()
        
        # Get response in separate thread
        threading.Thread(target=self.get_response, args=(message,), daemon=True).start()
    
    def get_response(self, message: str):
        """Get response from API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/personal-chatbot",
                "X-Title": "Desktop GUI Chatbot"
            }
            
            # System prompt
            system_prompt = (
                "You are a funny, witty, and natural human assistant. "
                "Always reply in the exact same language and style as the user (Hindi, English, Hinglish, Marathi, Gujarati, Tamil, etc). "
                "If the user mixes languages, you also mix naturally. "
                "Never reply in English if the user uses Hindi or Hinglish. "
                "Your answers must always match the user's language and tone, and be playful and human-like. "
                "Sometimes add a funny emoji or witty line."
            )
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            for msg in self.conversation_history[-8:]:
                messages.append(msg)
            
            messages.append({"role": "user", "content": message})
            
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.8,
                "max_tokens": 1000
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            assistant_message = result["choices"][0]["message"]["content"]
            
            # Add random emoji or witty line sometimes
            if random.random() < 0.3:
                if random.random() < 0.5:
                    assistant_message += " " + random.choice(BOT_EMOJIS)
                else:
                    assistant_message += "\n" + random.choice(BOT_WITTY)
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Update GUI in main thread
            self.root.after(0, self.update_response, assistant_message)
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.update_response, error_msg)
    
    def update_response(self, response: str):
        """Update GUI with response"""
        self.add_message("🤖 Assistant", response)
    
    def toggle_voice_input(self):
        """Toggle voice input"""
        if not self.voice_input_available:
            messagebox.showinfo("Voice Input", "Voice input is not available. Install PyAudio: pip install PyAudio")
            return
            
        if self.is_listening:
            self.is_listening = False
            self.voice_button.configure(text="🎤")
        else:
            self.is_listening = True
            self.voice_button.configure(text="⏹️")
            threading.Thread(target=self.listen_for_speech, daemon=True).start()
    
    def listen_for_speech(self):
        """Listen for voice input"""
        if not self.voice_input_available:
            return
            
        try:
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            
            text = self.recognizer.recognize_google(audio)
            
            # Update GUI in main thread
            self.root.after(0, self.process_voice_input, text)
            
        except sr.WaitTimeoutError:
            self.root.after(0, self.voice_input_timeout)
        except sr.UnknownValueError:
            self.root.after(0, self.voice_input_error, "Could not understand speech")
        except Exception as e:
            self.root.after(0, self.voice_input_error, str(e))
    
    def process_voice_input(self, text: str):
        """Process voice input"""
        self.is_listening = False
        self.voice_button.configure(text="🎤")
        
        # Add to input field
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, text)
        
        # Send message
        self.send_message()
    
    def voice_input_timeout(self):
        """Handle voice input timeout"""
        self.is_listening = False
        self.voice_button.configure(text="🎤")
        self.add_message("ℹ️ System", "Voice input timeout")
    
    def voice_input_error(self, error: str):
        """Handle voice input error"""
        self.is_listening = False
        self.voice_button.configure(text="🎤")
        self.add_message("ℹ️ System", f"Voice error: {error}")
    
    def clear_chat(self):
        """Clear chat display"""
        for widget in self.bubble_frame.winfo_children():
            widget.destroy()
        self.conversation_history.clear()
        self.add_message("🤖 Assistant", "Chat cleared. How can I help you? " + random.choice(BOT_EMOJIS))
        self.set_random_mood()

def main():
    """Main function"""
    root = tk.Tk()
    app = StylishChatbotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 