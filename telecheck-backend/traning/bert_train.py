import re
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Використовується пристрій: {device}")
df = pd.read_csv("/content/harmful_cleaned.xlsx - Worksheet(whout memes) (3).csv")


def clean_text(text):
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"@\w+", " ", text)
    text = re.sub(r"#\w+", " ", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"([a-z])([а-яєіїґ])", r"\1 \2", text)
    text = re.sub(r"([а-яєіїґ])([a-z])", r"\1 \2", text)
    text = re.sub(r"([a-zа-яєіїґ])(\d)", r"\1 \2", text)
    text = re.sub(r"(\d)([a-zа-яєіїґ])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


df['text'] = df['text'].apply(clean_text)

df.head()
df = df[['text', 'label']].dropna()
df = df.sample(frac=1).reset_index(drop=True)

texts = df['text'].tolist()
labels = df['label'].tolist()


train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)

model_name = "Geotrend/bert-base-uk-cased"
tokenizer = AutoTokenizer.from_pretrained(model_name)

class TelegramDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=512):
        self.encodings = tokenizer(texts, truncation=True, padding='max_length', max_length=max_len, return_tensors='pt')
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            'input_ids': self.encodings['input_ids'][idx],
            'attention_mask': self.encodings['attention_mask'][idx],
            'labels': self.labels[idx]
        }


train_dataset = TelegramDataset(train_texts, train_labels, tokenizer)
test_dataset = TelegramDataset(test_texts, test_labels, tokenizer)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=8)

model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)
model.to(device)

optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)


def train(model, dataloader, optimizer, device, epochs):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        num_batches = len(dataloader)
        print(f"\nEpoch {epoch + 1}/{epochs}")
        for i, batch in enumerate(dataloader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            total_loss += loss.item()

            loss.backward()
            optimizer.step()
            optimizer.zero_grad()

            percent = ((i + 1) / num_batches) * 100
            print(f"\rProgress: {percent:.1f}% — Batch {i+1}/{num_batches} — Loss: {loss.item():.4f}", end='', flush=True)

        print(f"\nEpoch {epoch + 1} Completed — Total Loss: {total_loss:.4f}")


def evaluate(model, dataloader, device):
    model.eval()
    preds = []
    true_labels = []
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids, attention_mask=attention_mask)
            logits = outputs.logits
            predictions = torch.argmax(logits, dim=1)

            preds.extend(predictions.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())

    print("\nEvaluation Report:")
    print(classification_report(true_labels, preds, digits=4))


if __name__ == "__main__":
    train(model, train_loader, optimizer, device, epochs=8)
    evaluate(model, test_loader, device)
    model.save_pretrained("saved_model/")
    tokenizer.save_pretrained("saved_model/")
