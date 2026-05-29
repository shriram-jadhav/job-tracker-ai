import fitz  # PyMuPDF
import spacy
import re

nlp = spacy.load('en_core_web_sm')

# Industry skills list — expand this as needed
SKILLS_DB = [
    # Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift',
    # Web
    'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'node.js', 'express',
    # Data / ML
    'machine learning', 'deep learning', 'nlp', 'computer vision', 'tensorflow', 'pytorch',
    'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'keras',
    # Databases
    'postgresql', 'mysql', 'mongodb', 'redis', 'sqlite', 'firebase',
    # DevOps / Cloud
    'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'git', 'github', 'ci/cd', 'linux',
    # Other
    'rest api', 'graphql', 'sql', 'html', 'css', 'tailwind', 'figma', 'agile', 'scrum'
]


def extract_text(pdf_path):
    """Extract raw text from PDF using PyMuPDF."""
    doc  = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()


def extract_skills(text):
    """Match skills from text against our skills database."""
    text_lower = text.lower()
    found = [skill for skill in SKILLS_DB if skill in text_lower]
    return list(set(found))  # remove duplicates


def extract_experience(text):
    """Extract years of experience using regex patterns."""
    patterns = [
        r'(\d+)\+?\s*years?\s+of\s+experience',
        r'(\d+)\+?\s*years?\s+experience',
        r'experience\s+of\s+(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yrs?\s+of\s+experience',
    ]
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    return None


def extract_education(text):
    """Extract education qualifications mentioned in resume."""
    degrees = [
        'b.e', 'b.tech', 'm.tech', 'm.e', 'bsc', 'msc',
        'bachelor', 'master', 'phd', 'mba', 'diploma'
    ]
    text_lower = text.lower()
    found = [deg.upper() for deg in degrees if deg in text_lower]
    return list(set(found))


def extract_certifications(text):
    """Extract common certifications."""
    certs = [
        'aws certified', 'google certified', 'azure certified',
        'pmp', 'scrum master', 'cissp', 'comptia',
        'tensorflow certificate', 'oracle certified'
    ]
    text_lower = text.lower()
    found = [cert.title() for cert in certs if cert in text_lower]
    return list(set(found))


def parse_resume(pdf_path):
    """Master function — runs full pipeline, returns structured dict."""
    text = extract_text(pdf_path)
    return {
        'raw_text':       text,
        'skills':         extract_skills(text),
        'experience_yrs': extract_experience(text),
        'education':      extract_education(text),
        'certifications': extract_certifications(text),
    }