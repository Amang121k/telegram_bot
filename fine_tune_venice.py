import torch
from transformers import (
    AutoTokenizer, 
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import json

def load_dataset():
    """Load custom Hindi/Hinglish dataset"""
    with open('hindi_hinglish_dataset.jsonl', 'r', encoding='utf-8') as f:
        data = [json.loads(line) for line in f]
    
    # Convert to training format
    formatted_data = []
    for item in data:
        text = f"{item['prompt']} {item['completion']}"
        formatted_data.append({"text": text})
    
    return Dataset.from_list(formatted_data)

def setup_model_and_tokenizer():
    """Setup Venice model and tokenizer"""
    model_name = "microsoft/DialoGPT-medium"  # Alternative to Venice for testing
    
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        load_in_8bit=True  # For memory efficiency
    )
    
    # Add padding token if not present
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    return model, tokenizer

def setup_lora_config():
    """Setup LoRA configuration for efficient fine-tuning"""
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,  # Rank
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"]
    )
    return lora_config

def tokenize_function(examples, tokenizer):
    """Tokenize the dataset"""
    return tokenizer(
        examples["text"],
        truncation=True,
        padding=True,
        max_length=512
    )

def main():
    print("🚀 Starting Venice Fine-tuning Setup...")
    
    # Load dataset
    print("📊 Loading dataset...")
    dataset = load_dataset()
    print(f"Dataset loaded: {len(dataset)} samples")
    
    # Setup model and tokenizer
    print("🤖 Setting up model and tokenizer...")
    model, tokenizer = setup_model_and_tokenizer()
    
    # Setup LoRA
    print("🔧 Setting up LoRA configuration...")
    lora_config = setup_lora_config()
    model = get_peft_model(model, lora_config)
    
    # Tokenize dataset
    print("🔤 Tokenizing dataset...")
    tokenized_dataset = dataset.map(
        lambda x: tokenize_function(x, tokenizer),
        batched=True,
        remove_columns=dataset.column_names
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./venice-hindi-bot",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        warmup_steps=100,
        learning_rate=2e-5,
        fp16=True,
        logging_steps=10,
        save_steps=500,
        eval_steps=500,
        evaluation_strategy="steps",
        save_strategy="steps",
        load_best_model_at_end=True,
        push_to_hub=False,
        report_to=None,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
    )
    
    # Start training
    print("🎯 Starting training...")
    trainer.train()
    
    # Save the model
    print("💾 Saving model...")
    trainer.save_model()
    tokenizer.save_pretrained("./venice-hindi-bot")
    
    print("✅ Training completed! Model saved in ./venice-hindi-bot/")

if __name__ == "__main__":
    main() 