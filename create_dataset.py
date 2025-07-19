import json
import random

# Custom Hindi/Hinglish Q&A Dataset for Telegram Bot
def create_custom_dataset():
    dataset = []
    
    # Telegram Bot Related Questions
    telegram_qa = [
        {
            "prompt": "User: Bot kaise banate hain?",
            "completion": "Bot banane ke liye @BotFather se contact karo. /newbot command use karo aur apna bot name aur username set karo."
        },
        {
            "prompt": "User: Token kya hota hai?",
            "completion": "Token bot ki unique ID hoti hai. @BotFather se milta hai. Isse bot control karte hain."
        },
        {
            "prompt": "User: Bot 24x7 kaise chalayen?",
            "completion": "Render, Railway, ya Heroku par deploy karo. Webhook set karo. Free hosting use karo."
        },
        {
            "prompt": "User: Webhook kya hai?",
            "completion": "Webhook Telegram ko batata hai ki bot kahan hosted hai. HTTPS URL chahiye hota hai."
        },
        {
            "prompt": "User: Bot mein error aa raha hai",
            "completion": "Logs check karo. API key sahi hai? Code mein syntax error to nahi? Debug karo."
        }
    ]
    
    # General Hindi/Hinglish Conversations
    general_qa = [
        {
            "prompt": "User: Kaise ho?",
            "completion": "Main theek hun! Aap kaise hain?"
        },
        {
            "prompt": "User: Aaj mausam kaisa hai?",
            "completion": "Aaj thoda cloudy hai. Barish ka chance hai."
        },
        {
            "prompt": "User: Kya haal hai?",
            "completion": "Sab badhiya! Kya plan hai aaj?"
        },
        {
            "prompt": "User: Time kya hua hai?",
            "completion": "Abhi 3 baje hain. Chai peene ka time ho gaya!"
        },
        {
            "prompt": "User: Kya kar rahe ho?",
            "completion": "Main yahan hun, aapki help ke liye ready hun!"
        }
    ]
    
    # Technical Questions in Hindi
    tech_qa = [
        {
            "prompt": "User: Python kya hai?",
            "completion": "Python ek programming language hai. Easy to learn, powerful hai. Web apps, AI, sab banate hain."
        },
        {
            "prompt": "User: API kya hoti hai?",
            "completion": "API ek service hai jo data exchange karti hai. Jaise weather API, payment API."
        },
        {
            "prompt": "User: Database kya hai?",
            "completion": "Database data store karne ka system hai. Jaise user info, messages sab save karta hai."
        },
        {
            "prompt": "User: Server kya hota hai?",
            "completion": "Server computer hai jo 24x7 online rehta hai. Websites, apps host karta hai."
        },
        {
            "prompt": "User: Code kaise likhte hain?",
            "Completion": "Pehle logic samjho, phir step by step likho. Practice karo, errors se seekho."
        }
    ]
    
    # Commands and Features
    commands_qa = [
        {
            "prompt": "User: /weather",
            "completion": "Aaj mausam thanda hai. 25°C temperature hai. Light breeze chal raha hai."
        },
        {
            "prompt": "User: /joke",
            "completion": "Ek joke suno: Programmer ne apni wife ko gift diya - 'Bug-free code'! 😄"
        },
        {
            "prompt": "User: /shayari",
            "completion": "Dil se niklegi na mar kar bhi watan ki ulfat, meri mitti se bhi khushboo-e-watan aayegi."
        },
        {
            "prompt": "User: /news",
            "completion": "Aaj ki top news: Tech companies ne AI development pe focus badhaya hai."
        }
    ]
    
    # Combine all datasets
    dataset.extend(telegram_qa)
    dataset.extend(general_qa)
    dataset.extend(tech_qa)
    dataset.extend(commands_qa)
    
    return dataset

def save_dataset():
    dataset = create_custom_dataset()
    
    # Save as JSON
    with open('hindi_hinglish_dataset.json', 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    # Save as JSONL (for training)
    with open('hindi_hinglish_dataset.jsonl', 'w', encoding='utf-8') as f:
        for item in dataset:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"Dataset created with {len(dataset)} samples")
    print("Files saved: hindi_hinglish_dataset.json, hindi_hinglish_dataset.jsonl")

if __name__ == "__main__":
    save_dataset() 