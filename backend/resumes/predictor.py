import joblib
import shap
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'ml_models', 'interview_predictor.pkl')
model = joblib.load(MODEL_PATH)

FEATURE_NAMES = ['fit_score', 'experience_yrs', 'skills_count', 'skill_gaps_count']

FEATURE_LABELS = {
    'fit_score':        'Resume–JD fit score',
    'experience_yrs':   'Years of experience',
    'skills_count':     'Number of skills on resume',
    'skill_gaps_count': 'Number of missing skills',
}


def predict_interview_probability(fit_score, experience_yrs, skills_count, skill_gaps_count):
    experience_yrs   = experience_yrs   or 0.0
    fit_score        = fit_score        or 0.0
    skills_count     = skills_count     or 0
    skill_gaps_count = skill_gaps_count or 0

    features = np.array([[fit_score, experience_yrs, skills_count, skill_gaps_count]])

    # ── Probability ───────────────────────────────────────────
    prob = float(model.predict_proba(features)[0][1])

    # ── SHAP explainability ───────────────────────────────────
    explainer   = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(features)

    # Handle both old SHAP (list of arrays) and new SHAP (single 3D array)
    if isinstance(shap_values, list):
        # Old SHAP: shap_values[1] = class 1
        shap_for_class1 = shap_values[1][0]
    else:
        # New SHAP: shape is (n_samples, n_features, n_classes)
        if shap_values.ndim == 3:
            shap_for_class1 = shap_values[0, :, 1]
        else:
            shap_for_class1 = shap_values[0]

    # ── Build human-readable summary ──────────────────────────
    shap_summary = []
    for i, fname in enumerate(FEATURE_NAMES):
        shap_summary.append({
            'feature': fname,
            'label':   FEATURE_LABELS[fname],
            'value':   round(float(features[0][i]), 2),
            'impact':  round(float(shap_for_class1[i]), 4),
        })

    shap_summary.sort(key=lambda x: abs(x['impact']), reverse=True)
    top_3 = shap_summary[:3]

    return round(prob, 4), top_3