from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re


def clean_text(text):
    """Lowercase, remove special characters, normalize whitespace."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def score_resume_jd(resume_text, jd_text):
    """
    Takes raw resume text and job description text.
    Returns a fit score between 0 and 100.
    """
    if not resume_text or not jd_text:
        return 0.0

    cleaned_resume = clean_text(resume_text)
    cleaned_jd     = clean_text(jd_text)

    # TF-IDF vectorizer — fits on both documents together
    vectorizer = TfidfVectorizer(
        stop_words='english',    # removes "the", "and", "is" etc.
        ngram_range=(1, 2),      # considers single words AND two-word phrases
        max_features=5000        # cap at 5000 most important terms
    )

    try:
        tfidf_matrix = vectorizer.fit_transform([cleaned_resume, cleaned_jd])
        similarity   = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score        = round(float(similarity[0][0]) * 100, 2)
        return score
    except Exception:
        return 0.0


def get_skill_gaps(resume_skills, jd_text):
    """
    Compare resume skills against JD text.
    Returns list of skills mentioned in JD but missing from resume.
    """
    # Common skills to look for in JD
    SKILLS_DB = [
        'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go',
        'react', 'angular', 'vue', 'django', 'flask', 'fastapi', 'node.js',
        'machine learning', 'deep learning', 'nlp', 'tensorflow', 'pytorch',
        'scikit-learn', 'pandas', 'numpy', 'postgresql', 'mysql', 'mongodb',
        'redis', 'docker', 'kubernetes', 'aws', 'gcp', 'azure', 'git',
        'rest api', 'graphql', 'sql', 'html', 'css', 'tailwind', 'agile'
    ]

    jd_lower          = jd_text.lower()
    resume_skills_low = [s.lower() for s in resume_skills]

    # Skills mentioned in JD but not in resume
    gaps = [
        skill for skill in SKILLS_DB
        if skill in jd_lower and skill not in resume_skills_low
    ]
    return gaps