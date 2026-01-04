import pandas as pd
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup
from sklearn.metrics import accuracy_score, f1_score, classification_report
import os
import json
import warnings

warnings.filterwarnings("ignore")

# --- CONFIGURATION ---
MODEL_NAME = "dbmdz/bert-base-turkish-cased"
MAX_LENGTH = 256
BATCH_SIZE = 4
EPOCHS = 6
LEARNING_RATE = 2e-5
DATA_DIR = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\dataset_splits"
OUTPUT_DIR = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\model_checkpoint"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- DATASET ---
class LGSDataset(Dataset):
    def __init__(self, df, tokenizer, label_maps, max_len=256):
        self.texts = df['text_input'].fillna("").values
        self.topic_labels = df['alt_konu'].values
        self.type_labels = df['soru_tipi'].values
        self.tokenizer = tokenizer
        self.max_len = max_len
        self.topic_map = label_maps['alt_konu']
        self.type_map = label_maps['soru_tipi']

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, item):
        text = str(self.texts[item])
        inputs = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_len,
            padding='max_length',
            return_token_type_ids=False,
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )

        topic_idx = self.topic_map.get(self.topic_labels[item], -1)
        type_idx = self.type_map.get(self.type_labels[item], -1)

        return {
            'input_ids': inputs['input_ids'].flatten(),
            'attention_mask': inputs['attention_mask'].flatten(),
            'topic_label': torch.tensor(topic_idx, dtype=torch.long),
            'type_label': torch.tensor(type_idx, dtype=torch.long)
        }

# --- MODEL ---
class MultiTaskBERT(nn.Module):
    def __init__(self, model_name, n_topics, n_types):
        super(MultiTaskBERT, self).__init__()
        self.bert = AutoModel.from_pretrained(model_name)
        self.drop = nn.Dropout(p=0.3)
        self.topic_out = nn.Linear(self.bert.config.hidden_size, n_topics)
        self.type_out = nn.Linear(self.bert.config.hidden_size, n_types)

    def forward(self, input_ids, attention_mask):
        outputs = self.bert(
            input_ids=input_ids,
            attention_mask=attention_mask
        )
        pooled_output = outputs.pooler_output
        output = self.drop(pooled_output)
        return self.topic_out(output), self.type_out(output)

# --- HELPER FUNCTIONS ---
def build_label_maps(train_df):
    topic_labels = sorted(train_df['alt_konu'].unique())
    type_labels = sorted(train_df['soru_tipi'].unique())
    
    label_maps = {
        'alt_konu': {label: idx for idx, label in enumerate(topic_labels)},
        'soru_tipi': {label: idx for idx, label in enumerate(type_labels)}
    }
    
    # Save maps
    with open(os.path.join(OUTPUT_DIR, 'label_map.json'), 'w', encoding='utf-8') as f:
        json.dump(label_maps, f, ensure_ascii=False, indent=4)
        
    return label_maps

def train_epoch(model, data_loader, optimizer, scheduler, device, n_examples):
    model = model.train()
    losses = []
    
    loss_fn = nn.CrossEntropyLoss()
    
    for d in data_loader:
        input_ids = d["input_ids"].to(device)
        attention_mask = d["attention_mask"].to(device)
        topic_targets = d["topic_label"].to(device)
        type_targets = d["type_label"].to(device)

        topic_preds, type_preds = model(
            input_ids=input_ids,
            attention_mask=attention_mask
        )

        loss_topic = loss_fn(topic_preds, topic_targets)
        loss_type = loss_fn(type_preds, type_targets)
        loss = loss_topic + loss_type

        losses.append(loss.item())

        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        scheduler.step()
        optimizer.zero_grad()

    return np.mean(losses)

def eval_model(model, data_loader, device, n_examples):
    model = model.eval()
    topic_preds_list = []
    type_preds_list = []
    topic_true_list = []
    type_true_list = []

    with torch.no_grad():
        for d in data_loader:
            input_ids = d["input_ids"].to(device)
            attention_mask = d["attention_mask"].to(device)
            
            topic_out, type_out = model(
                input_ids=input_ids,
                attention_mask=attention_mask
            )
            
            _, topic_preds = torch.max(topic_out, dim=1)
            _, type_preds = torch.max(type_out, dim=1)

            topic_preds_list.extend(topic_preds.cpu().numpy())
            type_preds_list.extend(type_preds.cpu().numpy())
            topic_true_list.extend(d["topic_label"].cpu().numpy())
            type_true_list.extend(d["type_label"].cpu().numpy())

    return topic_true_list, topic_preds_list, type_true_list, type_preds_list

def main():
    print(f"Using device: {DEVICE}")
    
    # Load Data
    train_df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
    val_df = pd.read_csv(os.path.join(DATA_DIR, 'val.csv'))
    
    # Build Maps
    label_maps = build_label_maps(train_df)
    n_topics = len(label_maps['alt_konu'])
    n_types = len(label_maps['soru_tipi'])
    print(f"Classes: {n_topics} Topics, {n_types} Types")

    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # Datasets
    train_dataset = LGSDataset(train_df, tokenizer, label_maps, MAX_LENGTH)
    val_dataset = LGSDataset(val_df, tokenizer, label_maps, MAX_LENGTH)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)

    # Model
    model = MultiTaskBERT(MODEL_NAME, n_topics, n_types)
    model = model.to(DEVICE)

    # Optimizer
    optimizer = AdamW(model.parameters(), lr=LEARNING_RATE)
    total_steps = len(train_loader) * EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=int(total_steps * 0.1),
        num_training_steps=total_steps
    )

    # Training Loop
    best_val_loss = float('inf')
    patience = 0
    
    for epoch in range(EPOCHS):
        print(f"\nEpoch {epoch + 1}/{EPOCHS}")
        print("-" * 10)
        
        train_loss = train_epoch(
            model, train_loader, optimizer, scheduler, DEVICE, len(train_df)
        )
        print(f"Train loss: {train_loss:.4f}")
        
        # Validation
        val_topic_true, val_topic_pred, val_type_true, val_type_pred = eval_model(
            model, val_loader, DEVICE, len(val_df)
        )
        
        # Calculate Validation Metrics (using weighted F1 as proxy for general performance)
        f1_topic = f1_score(val_topic_true, val_topic_pred, average='macro')
        f1_type = f1_score(val_type_true, val_type_pred, average='macro')
        val_score = (f1_topic + f1_type) / 2
        
        print(f"Val F1 Topic: {f1_topic:.4f}")
        print(f"Val F1 Type : {f1_type:.4f}")
        
        # Simple Early Stopping based on loss or F1? 
        # User said: "Validation Macro-F1 (alt_konu) izlenir"
        if f1_topic > best_val_loss: # Actually looking for max F1
             # We reuse best_val_loss var name as best_score for simplicity or make new one
             pass 
             
        # Just saving best model based on Topic F1 as requested
        # Note: logic inverted for loss, but F1 higher is better
        # Let's track best F1 Topic
        if not hasattr(main, "best_f1"): main.best_f1 = 0
        
        if f1_topic > main.best_f1:
            print("Validation F1 (Topic) improved. Saving model...")
            torch.save(model.state_dict(), os.path.join(OUTPUT_DIR, 'best_model.bin'))
            main.best_f1 = f1_topic
            patience = 0
        else:
            patience += 1
            print(f"No improvement. Patience {patience}/2")
            if patience >= 2:
                print("Early stopping triggered.")
                break

    print("Training complete.")

if __name__ == "__main__":
    main()
