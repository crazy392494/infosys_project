# Intelligent Career Recommendation Platform

A full-stack web application that helps job seekers upload resumes, analyze them using AI, identify strengths and missing skills, and receive personalized job recommendations.

## 🚀 Features

- **User Authentication**: Secure registration and login with password hashing
- **Resume Upload**: Support for PDF and DOCX file formats
- **AI-Powered Analysis**: 
  - Professional summary extraction
  - Technical and soft skills identification
  - Resume scoring (0-100)
  - Strengths and weaknesses analysis
  - Missing skills identification
  - Personalized improvement suggestions
- **Job Recommendations**: Smart matching algorithm that ranks jobs by relevance
- **Professional Dashboard**: Clean, modern UI with data visualizations
- **Favorites**: Save interesting job opportunities

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🛠️ Installation

1. **Navigate to the project directory**:
   ```bash
   cd c:\Users\Windows\infosys
   ```

2. **Install required packages** (if not already done):
   ```bash
   pip install -r requirements.txt
   ```

3. **Seed the database with sample jobs** (if not already done):
   ```bash
   python seed_jobs.py
   ```

## ▶️ Running the Application

1. **Start the Streamlit application**:
   ```bash
   streamlit run app.py
   ```

2. **Open your browser** and navigate to:
   ```
   http://localhost:8501
   ```

3. **Create an account** by registering with your details

4. **Upload your resume** (PDF or DOCX format)

5. **View your analysis** and job recommendations!

## 📂 Project Structure

```
infosys/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration and constants
├── database.py                 # Database setup and operations
├── auth.py                     # Authentication logic
├── resume_parser.py            # Resume text extraction
├── resume_analyzer.py          # AI analysis engine
├── job_matcher.py              # Recommendation algorithm
├── components.py               # Reusable UI components
├── seed_jobs.py                # Sample job data
├── requirements.txt            # Python dependencies
├── career_platform.db          # SQLite database (auto-generated)
└── uploads/                    # Resume file storage (auto-generated)
```

## 🎯 User Flow

1. **Register/Login** → Create account or sign in
2. **Upload Resume** → PDF or DOCX file
3. **AI Analysis** → Receive comprehensive resume analysis
4. **View Dashboard** → See score, skills, strengths, weaknesses
5. **Job Recommendations** → Browse matched opportunities
6. **Save Favorites** → Bookmark interesting jobs

## 🔧 Technology Stack

- **Frontend**: Streamlit with custom CSS
- **Backend**: Python
- **Database**: SQLite
- **Authentication**: bcrypt for password hashing
- **Resume Parsing**: PyPDF2, python-docx
- **Visualizations**: Plotly
- **AI Analysis**: Intelligent pattern matching and scoring algorithms

## 💡 Key Features Details

### Resume Analysis
- Extracts 50+ technical skills
- Identifies 25+ soft skills
- Calculates score based on:
  - Content quality (30%)
  - Technical skills (25%)
  - Experience (20%)
  - Education (15%)
  - Soft skills (10%)

### Job Matching
- Skill-based matching with synonym detection
- Direct and related skill matching
- Match percentage calculation
- Ranked recommendations

### Security
- Passwords hashed with bcrypt
- Session state management
- Email validation
- User-specific data isolation

## 🎨 UI Highlights

- Modern gradient-based design
- Interactive charts and gauges
- Responsive layout
- Smooth animations and transitions
- Professional color schemes
- Intuitive navigation

## 📝 Sample Resume Requirements

For best results, your resume should include:
- Professional summary or objective
- Technical skills section
- Work experience with descriptions
- Education and certifications
- Soft skills (teamwork, leadership, etc.)

## 🔄 Database Schema

- **Users**: User accounts and credentials
- **Resumes**: Uploaded resume data
- **Analysis**: AI analysis results
- **Jobs**: Job postings database
- **Recommendations**: User-job matches
- **Favorites**: Saved jobs

## 📊 Sample Data

The application comes pre-loaded with 15 diverse job postings including:
- Full Stack Developer
- Data Scientist
- DevOps Engineer
- Machine Learning Engineer
- Frontend/Backend Developers
- And more...

## 🛡️ File Upload Limits

- Maximum file size: 10MB
- Supported formats: PDF, DOCX, DOC
- Text extraction validation

## 🚧 Troubleshooting

**If database is locked:**
- Close all running instances of the app
- Delete `career_platform.db` and run `python seed_jobs.py` again

**If packages fail to install:**
- Try upgrading pip: `python -m pip install --upgrade pip`
- Install packages individually if batch install fails

**If resume upload fails:**
- Ensure file is not corrupted
- Check file format (PDF or DOCX)
- Verify file size is under 10MB

## 🎓 Future Enhancements

- PDF report generation
- Advanced skill visualizations
- Resume version comparison
- Integration with real job APIs
- LLM integration for enhanced analysis
- Email notifications
- Multi-language support

## 📄 License

This project is created for educational and demonstration purposes.

## 👨‍💻 Author

Built with ❤️ using Python and Streamlit

---

**Ready to boost your career? Start analyzing your resume today!** 🚀
