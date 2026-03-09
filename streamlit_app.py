import streamlit as st
import os
from groq import Groq
from PyPDF2 import PdfReader
from docx import Document

# Get API key from secrets (NOT hardcoded!)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY"))
if not GROQ_API_KEY:
    st.error("⚠️ Groq API key not found. Please set it in Streamlit secrets.")
    st.stop()
    
client = Groq(api_key=GROQ_API_KEY)

st.set_page_config(page_title="ATS Resume Analyzer", page_icon="📄", layout="wide")

# Custom CSS with enhanced styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .main-header {
        text-align: center;
        color: #2ecc71;
        padding: 20px;
        font-size: 2.5em;
    }
    .instruction-box {
        background-color: #000000;
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-left: 5px solid #2ecc71;
    }
    .instruction-box h3 {
        color: #2ecc71;
        margin-top: 0;
    }
    .instruction-box ul, .instruction-box ol {
        margin-bottom: 0;
    }
    .instruction-box li {
        margin: 5px 0;
    }
    .footer {
        text-align: center;
        padding: 20px;
        background-color: #f0f0f0;
        border-radius: 10px;
        margin-top: 30px;
        border-top: 3px solid #2ecc71;
    }
    .footer a {
        color: #2ecc71;
        text-decoration: none;
        font-weight: bold;
    }
    .footer a:hover {
        text-decoration: underline;
    }
    .stAlert {
        background-color: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    .stTextArea textarea {
        font-size: 14px;
        border: 2px solid #e0e0e0;
        border-radius: 5px;
        color: #000000 !important;
    }
    .stTextArea textarea:focus {
        border-color: #2ecc71;
        box-shadow: 0 0 5px rgba(46, 204, 113, 0.5);
    }
    .stMarkdown {
        color: #333333;
    }
    .results-box {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #2ecc71;
        margin-top: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .results-box h3 {
        color: #2ecc71;
        margin-top: 0;
    }
    .results-box p {
        color: #000000;
        line-height: 1.6;
    }
    .stButton button {
        background-color: #2ecc71;
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #27ae60;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("<h1 class='main-header'>📄 ATS Resume Analyzer</h1>", unsafe_allow_html=True)

# Initialize session state
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""

# Functions
def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text if text.strip() else "No text could be extracted from the PDF."
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(docx_file):
    """Extract text from DOCX file"""
    try:
        doc = Document(docx_file)
        text = ""
        for para in doc.paragraphs:
            if para.text.strip():
                text += para.text + "\n"
        return text if text.strip() else "No text could be extracted from the DOCX file."
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def generate_response(message, system_prompt, temperature, max_tokens):
    """Generate response using Groq API"""
    try:
        conversation = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=False
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Resume Analyzer Section
st.markdown("""
<div class='instruction-box'>
    <h3>📋 Instructions:</h3>
    <ul>
        <li>Upload your resume (PDF or DOCX) below.</li>
        <li>Check "Analyze with Job Description" if you have a specific job in mind.</li>
        <li>Paste the job description if applicable.</li>
        <li>Click "Analyze Resume" to get detailed ATS analysis.</li>
    </ul>
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    with_jd = st.checkbox("✅ Analyze with Job Description", value=True)
    if with_jd:
        job_description = st.text_area("📋 Job Description", height=150, placeholder="Paste the job description here...")
    uploaded_file = st.file_uploader("📤 Upload Resume (PDF or DOCX)", type=['pdf', 'docx'])
    
    if uploaded_file is not None:
        file_type = uploaded_file.name.split('.')[-1].lower()
        if file_type == 'pdf':
            st.session_state.resume_text = extract_text_from_pdf(uploaded_file)
        elif file_type == 'docx':
            st.session_state.resume_text = extract_text_from_docx(uploaded_file)
        st.success("✅ Resume uploaded successfully!")

with col2:
    st.text_area("📄 Parsed Resume Content", value=st.session_state.resume_text, height=300, disabled=True)

# Parameters in an expander
with st.expander("⚙️ Advanced Parameters"):
    col_temp, col_tokens = st.columns(2)
    with col_temp:
        temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.1,
                               help="Higher values make output more creative, lower more precise")
    with col_tokens:
        max_tokens = st.slider("Max Tokens", min_value=100, max_value=2048, value=1024, step=100,
                              help="Maximum length of the response")

if st.button("🚀 Analyze Resume", type="primary", use_container_width=True):
    if not st.session_state.resume_text:
        st.error("⚠️ Please upload a resume first.")
    elif with_jd and 'job_description' in locals() and not job_description:
        st.error("⚠️ Please enter a job description.")
    else:
        with st.spinner("🔄 Analyzing your resume..."):
            if with_jd and 'job_description' in locals():
                prompt = f"""
                Please analyze the following resume in the context of the job description provided. Strictly check every single line in the job description and analyze the resume for exact matches. Maintain high ATS standards and give scores only to the correct matches. Focus on missing core skills and soft skills. Provide the following details:
                1. The match percentage of the resume to the job description.
                2. A list of missing keywords.
                3. Final thoughts on the resume's overall match with the job description in 3 lines.
                4. Recommendations on how to add the missing keywords and improve the resume in 3-4 points with examples.
                
                Job Description: {job_description}
                
                Resume: {st.session_state.resume_text}
                """
            else:
                prompt = f"""
                Please analyze the following resume without a specific job description. Provide the following details:
                1. An overall score out of 10 for the resume.
                2. Suggestions for improvements based on the following criteria:
                   - Impact (quantification, repetition, verb usage, tenses, responsibilities, spelling & consistency)
                   - Brevity (length, bullet points, filler words)
                   - Style (buzzwords, dates, contact details, personal pronouns, active voice, consistency)
                   - Sections (summary, education, skills, unnecessary sections)
                3. A cumulative assessment of all the above fields.
                4. Recommendations for improving the resume in 3-4 points with examples.
                
                Resume: {st.session_state.resume_text}
                """
            
            response = generate_response(prompt, "You are an expert ATS resume analyzer.", temperature, max_tokens)
            st.markdown(f"""
            <div class='results-box'>
                <h3>📊 Analysis Results</h3>
                {response}
            </div>
            """, unsafe_allow_html=True)

st.markdown("""
<div class='footer'>
    <p>If you enjoyed the functionality of the app, please leave a like!<br>
    Check out more on <a href='https://www.linkedin.com/in/girish-wangikar/' target='_blank'>LinkedIn</a> | 
    <a href='https://girishwangikar.github.io/Girish_Wangikar_Portfolio.github.io/' target='_blank'>Portfolio</a></p>
</div>
""", unsafe_allow_html=True)