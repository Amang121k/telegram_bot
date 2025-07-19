# 🤖 Venice Model Fine-tuning for Hindi/Hinglish Telegram Bot

## 🎯 Overview
This setup allows you to fine-tune a language model (Venice-like) for Hindi/Hinglish conversations, specifically optimized for Telegram bot interactions.

## 📋 Prerequisites
- Python 3.8+
- 8GB+ RAM (16GB recommended)
- GPU with 8GB+ VRAM (optional, for faster training)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_finetune.txt
```

### 2. Create Custom Dataset
```bash
python3 create_dataset.py
```
This creates `hindi_hinglish_dataset.jsonl` with 19 custom Q&A samples.

### 3. Start Fine-tuning
```bash
python3 fine_tune_venice.py
```
Training will take 10-30 minutes depending on your hardware.

### 4. Test Fine-tuned Model
```bash
python3 test_finetuned_model.py
```

## 📊 Dataset Structure
The custom dataset includes:
- **Telegram Bot Q&A**: Bot creation, tokens, deployment
- **General Hindi/Hinglish**: Casual conversations
- **Technical Q&A**: Programming, APIs, databases
- **Commands**: /weather, /joke, /shayari, /news

## ⚙️ Configuration

### Model Settings
- **Base Model**: microsoft/DialoGPT-medium (Venice alternative)
- **Fine-tuning Method**: QLoRA (Low-RAM efficient)
- **Training Epochs**: 3
- **Learning Rate**: 2e-5
- **Batch Size**: 2 (with gradient accumulation)

### LoRA Configuration
- **Rank (r)**: 16
- **Alpha**: 32
- **Dropout**: 0.1
- **Target Modules**: q_proj, v_proj, k_proj, o_proj

## 📁 File Structure
```
personal_chatbot/
├── create_dataset.py          # Dataset creation script
├── fine_tune_venice.py        # Fine-tuning script
├── test_finetuned_model.py    # Model testing script
├── requirements_finetune.txt   # Fine-tuning dependencies
├── hindi_hinglish_dataset.jsonl # Custom dataset
└── venice-hindi-bot/          # Fine-tuned model (after training)
```

## 🔧 Customization

### Add More Training Data
Edit `create_dataset.py` and add more Q&A pairs:
```python
{
    "prompt": "User: Your question here?",
    "completion": "Your answer here."
}
```

### Adjust Training Parameters
In `fine_tune_venice.py`, modify:
- `num_train_epochs`: Training epochs
- `learning_rate`: Learning rate
- `per_device_train_batch_size`: Batch size

## 🎯 Expected Results
After fine-tuning, the model should:
- Respond in Hindi/Hinglish naturally
- Handle Telegram bot queries effectively
- Provide concise, relevant answers
- Support commands like /weather, /joke, etc.

## 🚨 Troubleshooting

### Memory Issues
- Reduce `per_device_train_batch_size` to 1
- Use `load_in_8bit=True` (already enabled)
- Close other applications during training

### Model Not Found
- Ensure training completed successfully
- Check `./venice-hindi-bot/` directory exists
- Verify model files are present

### Poor Results
- Increase training epochs
- Add more diverse training data
- Adjust learning rate
- Check dataset quality

## 🔄 Integration with Telegram Bot
After fine-tuning, integrate the model into your Telegram bot by:
1. Loading the fine-tuned model
2. Replacing OpenRouter API calls
3. Using local inference for responses

## 📈 Performance Tips
- Use GPU for faster training
- Increase dataset size for better results
- Experiment with different base models
- Fine-tune hyperparameters based on results

## 🤝 Contributing
Add more Hindi/Hinglish Q&A pairs to improve the model's conversational abilities! 