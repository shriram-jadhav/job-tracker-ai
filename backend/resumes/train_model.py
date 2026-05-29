import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# ── Reproducibility ───────────────────────────────────────────
np.random.seed(42)
N = 1000  # number of synthetic samples

# ── Generate synthetic training data ──────────────────────────
# Features: fit_score, experience_yrs, skills_count, skill_gaps_count
fit_scores        = np.random.uniform(0, 100, N)
experience_yrs    = np.random.uniform(0, 15,  N)
skills_count      = np.random.randint(3, 25,  N)
skill_gaps_count  = np.random.randint(0, 15,  N)

# Label: 1 = got interview, 0 = no interview
# Logic mirrors real-world patterns:
# high fit score + more experience + more skills + fewer gaps = higher chance
interview = (
    (fit_scores > 40).astype(int) * 3 +
    (experience_yrs > 2).astype(int) * 2 +
    (skills_count > 10).astype(int) * 2 +
    (skill_gaps_count < 5).astype(int) * 2 +
    np.random.randint(0, 3, N)  # some randomness
)
labels = (interview >= 5).astype(int)

# ── Build DataFrame ───────────────────────────────────────────
df = pd.DataFrame({
    'fit_score':       fit_scores,
    'experience_yrs':  experience_yrs,
    'skills_count':    skills_count,
    'skill_gaps_count': skill_gaps_count,
    'interview':       labels
})

X = df.drop('interview', axis=1)
y = df['interview']

# ── Train / test split ────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── Train Random Forest ───────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=6,
    random_state=42
)
model.fit(X_train, y_train)

# ── Evaluate ──────────────────────────────────────────────────
y_pred = model.predict(X_test)
print("\n── Model Evaluation ──")
print(classification_report(y_test, y_pred))

# ── Save model ───────────────────────────────────────────────
model_dir = os.path.join(os.path.dirname(__file__), 'ml_models')
os.makedirs(model_dir, exist_ok=True)
model_path = os.path.join(model_dir, 'interview_predictor.pkl')
joblib.dump(model, model_path)
print(f"\n✅ Model saved to {model_path}")