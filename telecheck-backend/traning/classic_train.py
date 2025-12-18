import pandas as pd
import re
import joblib
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
import os

def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

df = pd.read_csv("harmful_cleaned.xlsx - Worksheet(whout memes) (3).csv")
df = df[['text', 'label']].dropna()
df['text'] = df['text'].apply(clean_text)

X = df['text']
y = df['label']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

logreg_model = LogisticRegression(max_iter=1000)
logreg_model.fit(X_train_vec, y_train)
y_pred_lr = logreg_model.predict(X_test_vec)

print("=== Logistic Regression ===")
print("Accuracy:", accuracy_score(y_test, y_pred_lr))
print(classification_report(y_test, y_pred_lr, digits=3))

svm_model = SVC(kernel='linear', probability=True)
svm_model.fit(X_train_vec, y_train)
y_pred_svm = svm_model.predict(X_test_vec)

print("=== Support Vector Machine (SVM) ===")
print("Accuracy:", accuracy_score(y_test, y_pred_svm))
print(classification_report(y_test, y_pred_svm, digits=3))

os.makedirs("saved_classic_models", exist_ok=True)

joblib.dump(vectorizer, "saved_classic_models/tfidf_vectorizer.joblib")
joblib.dump(logreg_model, "saved_classic_models/logistic_regression_model.joblib")
joblib.dump(svm_model, "saved_classic_models/svm_model.joblib")

print("Моделі та векторизатор збережено.")