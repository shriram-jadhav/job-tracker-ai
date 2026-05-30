import re

# ── Action verbs considered strong ────────────────────────────
STRONG_VERBS = [
    'built', 'developed', 'designed', 'implemented', 'optimized',
    'led', 'managed', 'created', 'deployed', 'automated', 'reduced',
    'improved', 'increased', 'delivered', 'architected', 'integrated',
    'migrated', 'refactored', 'launched', 'scaled', 'streamlined',
    'engineered', 'collaborated', 'contributed', 'established'
]

# ── Weak/vague verbs to flag ───────────────────────────────────
WEAK_VERBS = [
    'worked', 'helped', 'assisted', 'did', 'made', 'used',
    'handled', 'involved', 'responsible', 'tried', 'attempted'
]

# ── Common JD keywords beyond skills ──────────────────────────
JD_KEYWORDS = [
    'agile', 'scrum', 'ci/cd', 'microservices', 'system design',
    'unit testing', 'code review', 'version control', 'documentation',
    'problem solving', 'communication', 'leadership', 'teamwork',
    'object oriented', 'data structures', 'algorithms', 'debugging'
]


def check_keyword_gaps(resume_text, jd_text):
    """Find important JD keywords missing from resume."""
    resume_lower = resume_text.lower()
    jd_lower     = jd_text.lower()

    missing = [
        kw for kw in JD_KEYWORDS
        if kw in jd_lower and kw not in resume_lower
    ]
    return missing


def check_weak_verbs(resume_text):
    """Find weak action verbs used in resume."""
    resume_lower = resume_text.lower()
    found_weak   = [v for v in WEAK_VERBS if v in resume_lower]
    return found_weak


def check_quantification(resume_text):
    """
    Check if resume has quantified achievements.
    Looks for numbers/percentages — their absence is a red flag.
    """
    has_numbers     = bool(re.search(r'\d+', resume_text))
    has_percentages = bool(re.search(r'\d+%', resume_text))
    has_metrics     = bool(re.search(
        r'(increased|reduced|improved|optimized).{0,30}\d+', resume_text.lower()
    ))
    return {
        'has_numbers':     has_numbers,
        'has_percentages': has_percentages,
        'has_metrics':     has_metrics,
    }


def generate_suggestions(resume_text, jd_text, skill_gaps):
    """
    Master function — returns structured list of suggestions.
    Each suggestion has a category, severity, and message.
    """
    suggestions = []

    # ── 1. Keyword gaps ───────────────────────────────────────
    keyword_gaps = check_keyword_gaps(resume_text, jd_text)
    if keyword_gaps:
        suggestions.append({
            'category': 'keywords',
            'severity': 'high',
            'message':  f"Add these keywords from the JD to your resume: {', '.join(keyword_gaps)}",
            'items':    keyword_gaps
        })

    # ── 2. Skill gaps ─────────────────────────────────────────
    if skill_gaps:
        suggestions.append({
            'category': 'skills',
            'severity': 'high',
            'message':  f"These skills are required in the JD but missing from your resume: {', '.join(skill_gaps)}",
            'items':    skill_gaps
        })

    # ── 3. Weak verbs ─────────────────────────────────────────
    weak = check_weak_verbs(resume_text)
    if weak:
        suggestions.append({
            'category': 'action_verbs',
            'severity': 'medium',
            'message':  f"Replace weak verbs ({', '.join(weak)}) with stronger ones like: built, developed, optimized, delivered, automated.",
            'items':    weak
        })

    # ── 4. Quantification ─────────────────────────────────────
    quant = check_quantification(resume_text)
    if not quant['has_metrics']:
        suggestions.append({
            'category': 'quantification',
            'severity': 'medium',
            'message':  "Add measurable impact to your bullet points. Example: 'Reduced API response time by 40%' instead of 'Improved API performance'.",
            'items':    []
        })
    if not quant['has_percentages']:
        suggestions.append({
            'category': 'quantification',
            'severity': 'low',
            'message':  "Include percentages or numbers to quantify achievements — recruiters respond strongly to metrics.",
            'items':    []
        })

    # ── 5. Positive feedback if strong ────────────────────────
    if not keyword_gaps and not skill_gaps:
        suggestions.append({
            'category': 'overall',
            'severity': 'positive',
            'message':  "Great match! Your resume covers the key skills and keywords in this JD.",
            'items':    []
        })

    return suggestions