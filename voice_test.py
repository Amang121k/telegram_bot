#!/usr/bin/env python3
import pyttsx3

def test_voices():
    """Test all available voices to find Hindi-compatible ones"""
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    
    print("🎤 Available Voices:")
    print("=" * 50)
    
    hindi_voices = []
    for i, voice in enumerate(voices):
        print(f"{i+1}. ID: {voice.id}")
        print(f"   Name: {voice.name}")
        print(f"   Languages: {voice.languages}")
        print(f"   Gender: {voice.gender}")
        print(f"   Age: {voice.age}")
        print("-" * 30)
        
        # Check if voice might support Hindi
        if any(keyword in voice.name.lower() for keyword in ['hindi', 'indian', 'asia', 'south']):
            hindi_voices.append(voice)
    
    print("\n🔍 Potential Hindi Voices:")
    if hindi_voices:
        for voice in hindi_voices:
            print(f"✅ {voice.name} ({voice.id})")
    else:
        print("❌ No Hindi-specific voices found")
    
    # Test with a Hindi sentence
    print("\n🧪 Testing Hindi pronunciation:")
    test_text = "नमस्ते, मैं आपकी मदद करने के लिए यहाँ हूँ"
    
    for voice in hindi_voices[:2]:  # Test first 2 Hindi voices
        print(f"\nTesting: {voice.name}")
        engine.setProperty('voice', voice.id)
        engine.setProperty('rate', 150)
        engine.say(test_text)
        engine.runAndWait()

if __name__ == "__main__":
    test_voices() 