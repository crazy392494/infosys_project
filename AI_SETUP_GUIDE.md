# AI Setup Guide - Get Your Free Gemini API Key

This application now uses **Google Gemini AI** to provide intelligent resume analysis and personalized recommendations!

## 🚀 Quick Setup (2 minutes)

### Step 1: Get Your Free API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click **"Create API Key"**
4. Copy your API key

### Step 2: Configure the API Key

**Option A: Environment Variable (Recommended)**

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GEMINI_API_KEY="your-api-key-here"
```

**Option B: Streamlit Secrets File**

Create `.streamlit/secrets.toml` with:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

Then update `ai_service.py` line 11 to:
```python
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', st.secrets.get("GEMINI_API_KEY", ""))
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Restart the Application

```bash
python -m streamlit run app.py
```

## ✨ AI Features

Once configured, you'll get:

### 🎯 **Intelligent Resume Analysis**
- Deep understanding of career trajectory
- Context-aware skill extraction
- Industry-specific insights

### 💡 **Personalized Recommendations**
- Tailored to your experience level
- Specific, actionable suggestions
- Prioritized by impact

### ✍️ **Professional Summary Generation**
- AI-written summaries
- ATS-optimized
- Highlights key strengths

### 📊 **Smart Skill Gap Analysis**
- Role-based comparisons
- Market demand insights
- Learning path recommendations

### 🚀 **AI Resume Enhancement**
- Improve summary statements
- Enhance experience descriptions
- Professional tone and impact

## 🔒 Privacy & Fallback

- ✅ Your resume data is sent to Google Gemini API for analysis
- ✅ Google's privacy policy applies
- ✅ If API key is not configured, app falls back to basic analysis
- ✅ All features work without AI, just with less intelligence

## 🆓 Free Tier Limits

Google Gemini API free tier includes:
- **15 requests per minute**
- **1,500 requests per day**
- **1 million tokens per day**

This is **more than enough** for personal resume analysis!

## ❓ Troubleshooting

**"⚠️ Gemini AI not configured" message?**
- Make sure you've set the `GEMINI_API_KEY` environment variable
- Restart your terminal/command prompt
- Restart the Streamlit app

**Still getting basic analysis?**
- Check that you copied the full API key
- Verify no extra spaces in the key
- Make sure you installed `google-generativeai` package

**API errors?**
- Check your API key is valid at https://aistudio.google.com/app/apikey
- Ensure you haven't exceeded free tier limits
- App will automatically fall back to basic analysis

## 📝 Example

**Without AI:**
> "Technology professional with experience in software development, demonstrating proficiency in various technical skills and tools."

**With AI:**
> "Results-driven Full-Stack Developer with 5+ years of experience building scalable web applications using React, Node.js, and AWS. Proven track record of architecting microservices solutions that improved system performance by 40% and reduced deployment time by 60%. Expertise in modern DevOps practices, passionate about clean code and continuous learning."

Much better! 🎉
