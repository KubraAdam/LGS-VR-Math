import torch
import pandas as pd
import numpy as np
import json
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from transformers import AutoTokenizer
from train_transformer import MultiTaskBERT, MODEL_NAME, MAX_LENGTH, DEVICE

# Config
DATA_DIR = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\dataset_splits"
CHECKPOINT_DIR = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\model_checkpoint"
OUTPUT_DIR = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\evaluation_results"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def load_resources():
    print("Loading resources...")
    # Label Map
    with open(os.path.join(CHECKPOINT_DIR, 'label_map.json'), 'r', encoding='utf-8') as f:
        label_maps = json.load(f)
    
    # Inverse Maps for decoding
    inv_topic_map = {v: k for k, v in label_maps['alt_konu'].items()}
    inv_type_map = {v: k for k, v in label_maps['soru_tipi'].items()}
    
    # Model
    model = MultiTaskBERT(MODEL_NAME, len(label_maps['alt_konu']), len(label_maps['soru_tipi']))
    model.load_state_dict(torch.load(os.path.join(CHECKPOINT_DIR, 'best_model.bin'), map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    
    # Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    return model, tokenizer, label_maps, inv_topic_map, inv_type_map

def predict(model, tokenizer, texts):
    print("Running predictions...")
    input_ids = []
    attention_masks = []
    
    for text in texts:
        encoded = tokenizer.encode_plus(
            str(text),
            add_special_tokens=True,
            max_length=MAX_LENGTH,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        input_ids.append(encoded['input_ids'])
        attention_masks.append(encoded['attention_mask'])
        
    input_ids = torch.cat(input_ids, dim=0).to(DEVICE)
    attention_masks = torch.cat(attention_masks, dim=0).to(DEVICE)
    
    # Predict in batches to avoid OOM
    batch_size = 8
    topic_preds = []
    type_preds = []
    
    with torch.no_grad():
        for i in range(0, len(input_ids), batch_size):
            batch_ids = input_ids[i:i+batch_size]
            batch_mask = attention_masks[i:i+batch_size]
            
            p_topic, p_type = model(batch_ids, batch_mask)
            
            topic_preds.extend(torch.argmax(p_topic, dim=1).cpu().numpy())
            type_preds.extend(torch.argmax(p_type, dim=1).cpu().numpy())
            
    return topic_preds, type_preds

def plot_confusion_matrix(y_true, y_pred, labels, title, filename):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title(title)
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, filename))
    print(f"Saved {filename}")

def main():
    # Load Test Data
    test_df = pd.read_csv(os.path.join(DATA_DIR, 'test.csv'))
    
    model, tokenizer, label_maps, inv_topic_map, inv_type_map = load_resources()
    
    # Get Predictions
    pred_topic_idxs, pred_type_idxs = predict(model, tokenizer, test_df['text_input'].tolist())
    
    # Decode Predictions
    test_df['pred_alt_konu'] = [inv_topic_map[i] for i in pred_topic_idxs]
    test_df['pred_soru_tipi'] = [inv_type_map[i] for i in pred_type_idxs]
    
    # 1. Classification Reports
    print("\n" + "="*30)
    print("TEST REPORT: ALT KONU (Topic)")
    print("="*30)
    report_topic = classification_report(test_df['alt_konu'], test_df['pred_alt_konu'])
    print(report_topic)
    
    print("\n" + "="*30)
    print("TEST REPORT: SORU TIPI (Type)")
    print("="*30)
    report_type = classification_report(test_df['soru_tipi'], test_df['pred_soru_tipi'])
    print(report_type)
    
    # 2. Confusion Matrices
    unique_topics = sorted(list(label_maps['alt_konu'].keys()))
    unique_types = sorted(list(label_maps['soru_tipi'].keys()))
    
    try:
        plot_confusion_matrix(test_df['alt_konu'], test_df['pred_alt_konu'], unique_topics, "Confusion Matrix - Alt Konu", "cm_alt_konu.png")
        plot_confusion_matrix(test_df['soru_tipi'], test_df['pred_soru_tipi'], unique_types, "Confusion Matrix - Soru Tipi", "cm_soru_tipi.png")
    except Exception as e:
        print(f"Could not plot confusion matrix (missing libraries?): {e}")

    # 3. Error Analysis
    # Get rows where EITHER topic OR type is wrong
    errors = test_df[
        (test_df['alt_konu'] != test_df['pred_alt_konu']) | 
        (test_df['soru_tipi'] != test_df['pred_soru_tipi'])
    ].copy()
    
    # --- NEW ANALYSES ---
    
    # A. Both Correct Rate
    both_correct = test_df[
        (test_df['alt_konu'] == test_df['pred_alt_konu']) & 
        (test_df['soru_tipi'] == test_df['pred_soru_tipi'])
    ]
    acc_both = len(both_correct) / len(test_df)
    print(f"\nBoth Correct Accuracy: {acc_both:.4f} ({len(both_correct)}/{len(test_df)})")
    
    # B. Visual Dependence Analysis
    if 'gorsel_bagimli' in test_df.columns:
        print("\nVisual Dependence Analysis:")
        # Normalize column (fill na, lower case)
        test_df['is_visual'] = test_df['gorsel_bagimli'].fillna('hayır').astype(str).apply(lambda x: 'bagimli' in x.lower() or 'var' in x.lower())
        
        for status in [True, False]:
            subset = test_df[test_df['is_visual'] == status]
            if len(subset) > 0:
                acc_topic = accuracy_score(subset['alt_konu'], subset['pred_alt_konu'])
                acc_type = accuracy_score(subset['soru_tipi'], subset['pred_soru_tipi'])
                label = "Visual Questions" if status else "Text-Only Questions"
                print(f"  {label} (n={len(subset)}): Topic Acc={acc_topic:.2f}, Type Acc={acc_type:.2f}")

    # C. Top Confused Pairs (Alt Konu)
    # We already have predictions, let's look at off-diagonal in confusion matrix logic
    cm_topic = confusion_matrix(test_df['alt_konu'], test_df['pred_alt_konu'], labels=unique_topics)
    
    confused_pairs = []
    for i, true_label in enumerate(unique_topics):
        for j, pred_label in enumerate(unique_topics):
            if i != j and cm_topic[i, j] > 0:
                confused_pairs.append({
                    "True": true_label,
                    "Predicted": pred_label,
                    "Count": int(cm_topic[i, j])
                })
    
    # Sort by count desc
    confused_pairs.sort(key=lambda x: x['Count'], reverse=True)
    print("\nTop 5 Confused Topic Pairs:")
    for cp in confused_pairs[:5]:
        print(f"  True: {cp['True']} -> Pred: {cp['Predicted']} (Count: {cp['Count']})")

    # D. Save JSON Metrics
    metrics = {
        "accuracy_both": acc_both,
        "classification_report_topic": classification_report(test_df['alt_konu'], test_df['pred_alt_konu'], output_dict=True),
        "classification_report_type": classification_report(test_df['soru_tipi'], test_df['pred_soru_tipi'], output_dict=True),
        "top_confused_pairs": confused_pairs[:10]
    }
    
    with open(os.path.join(OUTPUT_DIR, 'metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics, f, ensure_ascii=False, indent=4)
    print(f"\nSaved metrics.json to {OUTPUT_DIR}")

    print(f"\nTotal Errors: {len(errors)} out of {len(test_df)} test samples ({len(errors)/len(test_df):.2%})")
    
    # Select important columns
    cols = ['soru_metin', 'alt_konu', 'pred_alt_konu', 'soru_tipi', 'pred_soru_tipi']
    error_report_path = os.path.join(OUTPUT_DIR, 'error_analysis.csv')
    errors[cols].to_csv(error_report_path, index=False)
    print(f"Error analysis saved to {error_report_path}")
    
    # Show first 5 errors
    print("\nSample Errors:")
    print(errors[cols].head(5).to_markdown(index=False))

if __name__ == "__main__":
    main()
