# Switching Between LLM Providers (Groq ↔ OpenAI)

## 🎯 Overview

Your project is **100% compatible** with both Groq and OpenAI GPT models. You can switch between them in seconds by simply changing your `.env` file configuration.

## ✅ How to Switch

### Step 1: Update your `.env` file

**Option A: Use Groq (Current Default)**
```bash
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

**Option B: Switch to OpenAI GPT**
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your_openai_api_key_here
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
```

### Step 2: Restart the backend server
```bash
cd backend
python -m uvicorn app.main:app --reload
```

**That's it!** No code changes needed. The project automatically detects your provider and uses the correct model.

---

## 🚀 Supported Models

### Groq Models
- **llama-3.3-70b-versatile** ⭐ (Recommended - Best quality)
- **llama-3.1-8b-instant** (Faster, good for testing)
- **mixtral-8x7b-32768** (Fallback with large context)

### OpenAI Models
- **gpt-4o** ⭐ (Recommended - Latest GPT-4 Optimized)
- **gpt-4o-mini** (Faster, cheaper, still excellent)
- **gpt-4-turbo** (Previous generation)
- **gpt-3.5-turbo** (Fastest, most economical)

---

## 🔍 Verification

### Check Current Provider
Visit the health endpoint:
```bash
curl http://localhost:8000/api/v1/health
```

Response will show:
```json
{
  "status": "healthy",
  "llm_provider": "groq",  // or "openai"
  "llm_model": "llama-3.3-70b-versatile",  // or "gpt-4o"
  "llm_status": "available",
  "vector_store": "available"
}
```

### Test from Python
```python
from app.services.llm_service import llm_service

info = llm_service.get_provider_info()
print(f"Provider: {info['provider']}")
print(f"Model: {info['model']}")
print(f"Status: {info['status']}")
```

---

## ⚙️ Technical Details

### How It Works
1. **Configuration**: `app/core/config.py` reads `LLM_PROVIDER` from `.env`
2. **Service Layer**: `app/services/llm_service.py` initializes the correct LLM:
   - If `LLM_PROVIDER=groq` → Uses `ChatGroq` from `langchain-groq`
   - If `LLM_PROVIDER=openai` → Uses `ChatOpenAI` from `langchain-openai`
3. **RAG Engine**: `app/core/rag_engine_pro.py` uses the service without knowing which provider is active
4. **Zero Changes**: Frontend, routes, and all other code work identically with both providers

### Dependencies Already Installed
```
✅ langchain-groq    # For Groq
✅ langchain-openai  # For OpenAI
✅ langchain-core    # Unified interface
```

---

## 💡 Best Practices

### Cost Optimization
- **Development/Testing**: Use `groq` (free tier available) or `gpt-4o-mini`
- **Production**: Use `gpt-4o` for best quality or `groq` for speed

### Quality vs Speed
- **Highest Quality**: `gpt-4o` (OpenAI)
- **Best Balance**: `llama-3.3-70b-versatile` (Groq)
- **Fastest**: `llama-3.1-8b-instant` (Groq) or `gpt-3.5-turbo` (OpenAI)

### Automatic Fallback
The system includes automatic fallback:
1. Tries your primary model
2. If it fails, tries alternative models
3. Graceful error handling

---

## 🐛 Troubleshooting

### "API Key not found"
- **Groq**: Ensure `GROQ_API_KEY` is set in `.env`
- **OpenAI**: Ensure `OPENAI_API_KEY` is set in `.env`
- Restart the server after changing `.env`

### "Model not available"
- Check your API key has access to the specified model
- Try a different model from the supported list

### Rate Limits
- **Groq**: Free tier has generous limits
- **OpenAI**: Upgrade your account tier if needed
- Consider switching providers temporarily if limits are reached

---

## 📊 Comparison Table

| Feature | Groq | OpenAI GPT |
|---------|------|------------|
| **Speed** | ⚡⚡⚡ Very Fast | ⚡⚡ Fast |
| **Quality** | ⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐⭐ Best |
| **Cost** | 💰 Free tier available | 💰💰 Pay-per-token |
| **Context Window** | 32K-128K tokens | 128K tokens |
| **Setup** | ✅ Already configured | ✅ Already configured |
| **Switching** | Change 1 line in .env | Change 1 line in .env |

---

## ✨ Summary

**YES**, your project is fully switchable between Groq and OpenAI GPT:

1. ✅ **No code changes required** - Just update `.env`
2. ✅ **Both providers pre-configured** - Dependencies already installed
3. ✅ **Automatic detection** - System picks the right provider
4. ✅ **Production-ready** - Error handling and fallbacks included
5. ✅ **Zero downtime** - Just restart the server

**To switch to OpenAI GPT right now:**
```bash
# Edit backend/.env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-your_actual_key_here
OPENAI_MODEL=gpt-4o

# Restart backend
cd backend
python -m uvicorn app.main:app --reload
```

Done! Your chatbot now uses OpenAI GPT instead of Groq. Switch back anytime by changing `LLM_PROVIDER=groq`.
