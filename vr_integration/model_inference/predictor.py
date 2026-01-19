"""
Model Predictor
Loads trained model and makes predictions on question text
"""

import os
import json
import torch
from transformers import AutoTokenizer
from typing import Dict, Tuple, Optional
import sys

# Add parent directory to path to import train_transformer
sys.path.append(os.path.join(os.path.dirname(__file__), '../../modeleğitimi'))

try:
    from train_transformer import MultiTaskBERT, MODEL_NAME, MAX_LENGTH, DEVICE
except ImportError:
    # Fallback if import fails
    MODEL_NAME = "dbmdz/bert-base-turkish-cased"
    MAX_LENGTH = 256
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class ModelPredictor:
    """
    Model Predictor Service
    
    Loads trained BERT model and provides prediction interface
    """
    
    def __init__(
        self,
        checkpoint_dir: Optional[str] = None,
        model_path: Optional[str] = None
    ):
        """
        Initialize predictor
        
        Args:
            checkpoint_dir: Directory containing label_map.json and best_model.bin
            model_path: Direct path to model file (overrides checkpoint_dir)
        """
        if checkpoint_dir is None:
            # Default path
            checkpoint_dir = os.path.join(
                os.path.dirname(__file__),
                '../../modeleğitimi/model_checkpoint'
            )
        
        self.checkpoint_dir = checkpoint_dir
        self.model_path = model_path or os.path.join(checkpoint_dir, 'best_model.bin')
        
        self.model = None
        self.tokenizer = None
        self.label_maps = None
        self.inv_topic_map = None
        self.inv_type_map = None
        
        self._load_model()
    
    def _load_model(self):
        """Load model, tokenizer, and label maps"""
        print(f"Loading model from {self.checkpoint_dir}...")
        
        # Load label maps
        label_map_path = os.path.join(self.checkpoint_dir, 'label_map.json')
        if not os.path.exists(label_map_path):
            raise FileNotFoundError(
                f"Label map not found at {label_map_path}. "
                "Please train the model first."
            )
        
        with open(label_map_path, 'r', encoding='utf-8') as f:
            self.label_maps = json.load(f)
        
        # Create inverse maps
        self.inv_topic_map = {
            v: k for k, v in self.label_maps['alt_konu'].items()
        }
        self.inv_type_map = {
            v: k for k, v in self.label_maps['soru_tipi'].items()
        }
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        
        # Load model
        n_topics = len(self.label_maps['alt_konu'])
        n_types = len(self.label_maps['soru_tipi'])
        
        self.model = MultiTaskBERT(MODEL_NAME, n_topics, n_types)
        
        if os.path.exists(self.model_path):
            self.model.load_state_dict(
                torch.load(self.model_path, map_location=DEVICE)
            )
            print(f"Model loaded from {self.model_path}")
        else:
            print(f"Warning: Model file not found at {self.model_path}")
            print("Using untrained model (predictions will be random)")
        
        self.model.to(DEVICE)
        self.model.eval()
        
        print("Model loaded successfully!")
    
    def predict(
        self,
        text_input: str,
        return_probs: bool = False
    ) -> Dict:
        """
        Predict alt_konu and soru_tipi from question text
        
        Args:
            text_input: Formatted question text (same format as training)
            return_probs: If True, also return probability distributions
            
        Returns:
            Dict with:
                - alt_konu: str
                - soru_tipi: str
                - confidence: float (optional)
                - probabilities: dict (optional)
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call _load_model() first.")
        
        # Tokenize
        encoded = self.tokenizer.encode_plus(
            str(text_input),
            add_special_tokens=True,
            max_length=MAX_LENGTH,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        input_ids = encoded['input_ids'].to(DEVICE)
        attention_mask = encoded['attention_mask'].to(DEVICE)
        
        # Predict
        with torch.no_grad():
            topic_out, type_out = self.model(input_ids, attention_mask)
            
            topic_probs = torch.softmax(topic_out, dim=1)
            type_probs = torch.softmax(type_out, dim=1)
            
            topic_pred_idx = torch.argmax(topic_probs, dim=1).item()
            type_pred_idx = torch.argmax(type_probs, dim=1).item()
            
            topic_confidence = topic_probs[0, topic_pred_idx].item()
            type_confidence = type_probs[0, type_pred_idx].item()
        
        # Decode
        alt_konu = self.inv_topic_map.get(topic_pred_idx, "Unknown")
        soru_tipi = self.inv_type_map.get(type_pred_idx, "Unknown")
        
        result = {
            "alt_konu": alt_konu,
            "soru_tipi": soru_tipi,
            "confidence": {
                "alt_konu": topic_confidence,
                "soru_tipi": type_confidence
            }
        }
        
        if return_probs:
            result["probabilities"] = {
                "alt_konu": {
                    self.inv_topic_map[i]: topic_probs[0, i].item()
                    for i in range(len(self.inv_topic_map))
                },
                "soru_tipi": {
                    self.inv_type_map[i]: type_probs[0, i].item()
                    for i in range(len(self.inv_type_map))
                }
            }
        
        return result
    
    def format_question_input(
        self,
        soru_metin: str,
        secenekler: Optional[Dict[str, str]] = None,
        gorsel_bagimli: Optional[str] = None
    ) -> str:
        """
        Format question text in the same way as training data
        
        Args:
            soru_metin: Question text
            secenekler: Dict with keys A, B, C, D, E
            gorsel_bagimli: Visual dependency flag
            
        Returns:
            Formatted text input
        """
        text = f"[SORU] {soru_metin}\n"
        
        if secenekler:
            for opt in ['A', 'B', 'C', 'D', 'E']:
                if opt in secenekler and secenekler[opt]:
                    text += f"[{opt}] {secenekler[opt]}\n"
        
        if gorsel_bagimli:
            val = str(gorsel_bagimli).lower()
            if 'bagimli' in val or 'var' in val:
                text += "[GÖRSEL] Bu soru görsele bağlıdır.\n"
        
        return text.strip()


# Singleton instance
_predictor = None

def get_predictor(checkpoint_dir: Optional[str] = None) -> ModelPredictor:
    """Get singleton predictor instance"""
    global _predictor
    if _predictor is None:
        _predictor = ModelPredictor(checkpoint_dir)
    return _predictor

