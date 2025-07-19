import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel
import json

def load_finetuned_model():
    """Load the fine-tuned model"""
    base_model_path = "./venice-hindi-bot"
    
    try:
        tokenizer = AutoTokenizer.from_pretrained(base_model_path)
        model = AutoModelForCausalLM.from_pretrained(
            base_model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        return model, tokenizer
    except Exception as e:
        print(f"Model not found: {e}")
        return None, None

def generate_response(model, tokenizer, prompt, max_length=100):
    """Generate response from fine-tuned model"""
    inputs = tokenizer.encode(prompt, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_length=max_length,
            num_return_sequences=1,
            temperature=0.7,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def test_conversations():
    """Test the model with various Hindi/Hinglish prompts"""
    model, tokenizer = load_finetuned_model()
    
    if model is None:
        print("❌ Model not found. Please run fine-tuning first.")
        return
    
    test_prompts = [
        "User: Bot kaise banate hain?",
        "User: Kaise ho?",
        "User: /weather",
        "User: /joke",
        "User: Python kya hai?",
        "User: Token kya hota hai?"
    ]
    
    print("🧪 Testing Fine-tuned Model...")
    print("=" * 50)
    
    for prompt in test_prompts:
        print(f"Prompt: {prompt}")
        response = generate_response(model, tokenizer, prompt)
        print(f"Response: {response}")
        print("-" * 30)

if __name__ == "__main__":
    test_conversations() 