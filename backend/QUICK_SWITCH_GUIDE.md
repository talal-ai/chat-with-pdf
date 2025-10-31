# 🔄 Quick Provider Switching Guide

## Current Status
✅ **Groq** and **OpenAI** are both fully supported  
✅ No code changes needed to switch  
✅ Just update `.env` and restart the server

---

## Switch to OpenAI GPT (1 minute)

### 1. Edit `backend/.env`
```bash
# Change this line:
LLM_PROVIDER=openai

# Add your OpenAI key:
OPENAI_API_KEY=sk-your_actual_openai_api_key_here

# Choose model (optional):
OPENAI_MODEL=gpt-4o
```

### 2. Restart backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

### 3. Verify
Visit: http://localhost:8000/api/v1/health

Should show:
```json
{
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "llm_status": "available"
}
```

---

## Switch Back to Groq

### 1. Edit `backend/.env`
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

### 2. Restart backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

---

## Recommended Models

### For Production (Best Quality)
```bash
# OpenAI
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o

# OR Groq
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.3-70b-versatile
```

### For Development (Faster/Cheaper)
```bash
# OpenAI
LLM_PROVIDER=openai
OPENAI_MODEL=gpt-4o-mini

# OR Groq
LLM_PROVIDER=groq
GROQ_MODEL=llama-3.1-8b-instant
```

---

## Troubleshooting

### Issue: "API Key not found"
**Solution**: Make sure the API key is set in `.env` and restart the server

### Issue: "Model not available"
**Solution**: Check if your API key has access to the model, or try a different model

### Issue: Changes not taking effect
**Solution**: Restart the backend server after editing `.env`

---

## Summary

✨ **You can switch providers anytime!**
- No code changes
- No data loss
- No configuration hassle
- Just 1 line in `.env`

Currently using: **Groq (llama-3.3-70b-versatile)**  
To switch: Change `LLM_PROVIDER=openai` in `.env` and restart
