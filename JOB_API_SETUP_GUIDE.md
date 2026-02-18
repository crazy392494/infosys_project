# Live Job Search Setup Guide

Get your resume analyzer to show **real, current job postings** from companies worldwide!

## 🚀 Quick Setup (3 minutes)

### Step 1: Create Free Adzuna Account

1. Visit [Adzuna Developer Portal](https://developer.adzuna.com/)
2. Click **"Create new account"**
3. Fill in your details
4. Verify your email

### Step 2: Get API Credentials

1. Log in to [Adzuna Developer Portal](https://developer.adzuna.com/)
2. You'll see your credentials on the dashboard:
   - **Application ID** (looks like: `12345678`)
   - **API Key** (looks like: `abcd1234ef5678gh`)
3. Copy both values

### Step 3: Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:ADZUNA_APP_ID = "your_app_id_here"
$env:ADZUNA_API_KEY = "your_api_key_here"
```

**Windows (Command Prompt):**
```cmd
set ADZUNA_APP_ID=your_app_id_here
set ADZUNA_API_KEY=your_api_key_here
```

**Linux/Mac:**
```bash
export ADZUNA_APP_ID="your_app_id_here"
export ADZUNA_API_KEY="your_api_key_here"
```

### Step 4: Restart the Application

```bash
python -m streamlit run app.py
```

## ✨ What You Get

Once configured, your app will show:

### 🔴 **Live Job Postings**
- Real jobs from actual companies
- Posted in the last 30 days
- Direct apply links

### 💰 **Salary Information**
- Salary ranges when available
- Updated hourly rates
- Benefits information

### 📍 **Location & Remote Jobs**
- City/state locations
- Remote work indicators
- Hybrid options

### 📅 **Posting Freshness**
- "Just posted" for new jobs
- "X days ago" timestamps
- Only fresh opportunities

### 🎯 **Smart Matching**
- Jobs matched to YOUR skills
- Match percentage based on resume
- Required vs. preferred skills

## 🆓 Free Tier Limits

Adzuna free tier includes:
- ✅ **1,000 API calls/month**
- ✅ **Jobs from multiple sources**
- ✅ **No credit card required**

**Typical usage:**
- 1 job search = 1 API call
- Average: 10 jobs per search
- **Free tier supports ~100 job search sessions/month**

Perfect for job hunting! 🎉

## 🌍 Supported Countries

Change `DEFAULT_COUNTRY` in `config.py` to:
- `'us'` - United States
- `'gb'` - United Kingdom
- `'in'` - India
- `'ca'` - Canada
- `'au'` - Australia
- `'de'` - Germany
- `'fr'` - France
- `'nl'` - Netherlands
- `'br'` - Brazil
- And many more!

## 🎨 What It Looks Like

**Without API (Mock Data):**
```
Software Engineer - TechCorp
Location: Remote
[Generic description]
```

**With Live API:**
```
🔴 LIVE Senior Full-Stack Developer - Google
Google • Remote
💰 $120,000 - $180,000 • 📅 2 days ago • 📝 Full-time
Match: 85%

[Real job description from Google]
[Apply Now →] (direct link)
```

## ❓ Troubleshooting

**"⚠️ Adzuna API not configured"**
- Make sure you set both `ADZUNA_APP_ID` and `ADZUNA_API_KEY`
- Restart your terminal/PowerShell
- Restart the Streamlit app

**Still showing mock jobs?**
- Check you copied the credentials correctly
- Verify no extra spaces in the values
- Try setting them directly in `config.py` (lines 114-115)

**API errors?**
- Check your API key is valid at https://developer.adzuna.com/
- Ensure you haven't exceeded the 1,000 calls/month limit
- App will automatically fall back to mock data

**No jobs showing?**
- Try different search keywords
- Check if your country is supported
- The app extracts skills from your resume to search

## 🔒 Privacy Note

When you use the live API:
- Your search keywords (skills) are sent to Adzuna
- Adzuna's privacy policy applies
- No personal information is sent
- Resume content stays local

## 💡 Tips for Best Results

1. **Upload a detailed resume** - More skills = better job matching
2. **Keep skills updated** - Add latest technologies to your resume
3. **Check regularly** - New jobs are posted daily
4. **Set your country** - Edit `DEFAULT_COUNTRY` in `config.py`

## 🎯 Without API Key?

Don't have an API key yet? **No problem!**
- App shows mock job data as examples
- All features still work
- Get API key when ready for real jobs

---

**Ready to find your dream job?** Set up your API and start seeing real opportunities! 🚀
