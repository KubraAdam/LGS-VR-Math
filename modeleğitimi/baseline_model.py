import pandas as pd
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

DATA_DIR = r"C:\Users\Serhat PAMUK\Desktop\modeleğitimi\dataset_splits"

def load_data():
    print("Loading data splits...")
    try:
        train_df = pd.read_csv(os.path.join(DATA_DIR, 'train.csv'))
        test_df = pd.read_csv(os.path.join(DATA_DIR, 'test.csv'))
        # We can also load val if we want to tune, but for baseline we might just test on test set
        # But sticking to plan: Train on Train, Eval on Test for report.
        return train_df, test_df
    except FileNotFoundError:
        print(f"Error: Data files not found in {DATA_DIR}. Please run data_prep.py first.")
        return None, None

def train_and_evaluate(train_df, test_df):
    # Features
    X_train = train_df['text_input'].fillna("")
    X_test = test_df['text_input'].fillna("")
    
    print("\nVectorizing text (TF-IDF)...")
    vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=10000)
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    # Targets
    targets = ['alt_konu', 'soru_tipi']
    
    results = {}
    
    for target in targets:
        print(f"\n{'='*30}")
        print(f"Training Baseline for Target: {target}")
        print(f"{'='*30}")
        
        y_train = train_df[target]
        y_test = test_df[target]
        
        # Model: Logistic Regression (strong baseline)
        clf = LogisticRegression(class_weight='balanced', max_iter=1000, multi_class='auto', solver='lbfgs')
        clf.fit(X_train_vec, y_train)
        
        # Prediction
        y_pred = clf.predict(X_test_vec)
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {acc:.4f}")
        
        report = classification_report(y_test, y_pred)
        print("\nClassification Report:")
        print(report)
        
        # Store for summary if needed
        results[target] = report
        
    return results

def main():
    if not os.path.exists(DATA_DIR):
        print(f"Directory {DATA_DIR} does not exist. Run data_prep.py first.")
        return

    train_df, test_df = load_data()
    if train_df is not None:
        train_and_evaluate(train_df, test_df)

if __name__ == "__main__":
    main()
