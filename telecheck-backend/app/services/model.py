import torch
import joblib
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print("Завантаження BERT...")
bert_model = AutoModelForSequenceClassification.from_pretrained("C:/Users/Dream Store/Desktop/TeleCheckAI/telecheck-backend/saved_model6").to(device)
bert_tokenizer = AutoTokenizer.from_pretrained("C:/Users/Dream Store/Desktop/TeleCheckAI/telecheck-backend/saved_model6")
print("BERT завантажено.")

print("Завантаження класичних моделей...")
logreg = joblib.load("C:/Users/Dream Store/Desktop/TeleCheckAI/telecheck-backend/saved_classic_models/logistic_regression_model.joblib")
svm = joblib.load("C:/Users/Dream Store/Desktop/TeleCheckAI/telecheck-backend/saved_classic_models/svm_model.joblib")
vectorizer = joblib.load("C:/Users/Dream Store/Desktop/TeleCheckAI/telecheck-backend/saved_classic_models/tfidf_vectorizer.joblib")
print("Класичні моделі завантажено.")

def predict_bert(text: str) -> int:
    inputs = bert_tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        logits = bert_model(**inputs).logits
        prediction = torch.argmax(logits, dim=1).item()
    return prediction

def predict_logreg(text: str) -> int:
    vec = vectorizer.transform([text])
    return logreg.predict(vec)[0]

def predict_svm(text: str) -> int:
    vec = vectorizer.transform([text])
    return svm.predict(vec)[0]

def predict_with_voting(text: str) -> int:
    votes = [
        predict_bert(text),
        predict_logreg(text),
        predict_svm(text)
    ]
    majority_vote = int(np.round(np.mean(votes)))  # 0 якщо <= 1, 1 якщо >= 2
    print(f"BERT: {votes[0]}, LogisticRegression: {votes[1]}, SVM: {votes[2]} → Рішення: {majority_vote}")
    return majority_vote

