"""
Question Generator
Loads questions from dataset and provides random question selection
"""

import pandas as pd
import os
import random
from typing import Dict, Optional

class QuestionGenerator:
    """
    Question Generator Service
    
    Loads questions from dataset and provides random selection
    """
    
    def __init__(self, dataset_path: Optional[str] = None):
        """
        Initialize question generator
        
        Args:
            dataset_path: Path to dataset CSV file
        """
        if dataset_path is None:
            # Default path - use train.csv
            dataset_path = os.path.join(
                os.path.dirname(__file__),
                '../../modeleğitimi/dataset_splits/train.csv'
            )
        
        self.dataset_path = dataset_path
        self.df = None
        self._load_dataset()
    
    def _load_dataset(self):
        """Load dataset from CSV"""
        try:
            print(f"Loading questions from {self.dataset_path}...")
            self.df = pd.read_csv(self.dataset_path)
            print(f"Loaded {len(self.df)} questions")
        except Exception as e:
            print(f"Error loading dataset: {e}")
            self.df = None
    
    def get_random_question(self, gorsel_filter: Optional[str] = None) -> Optional[Dict]:
        """
        Get a random question from dataset
        
        Args:
            gorsel_filter: Filter by visual dependency
                - "bagimli": Only visual dependent questions
                - "bagimsiz": Only visual independent questions
                - "destekleyici": Only supporting visual questions
                - None: All questions
        
        Returns:
            Dict with question data or None if dataset not loaded
        """
        if self.df is None or len(self.df) == 0:
            return None
        
        # Filter by visual dependency if specified
        filtered_df = self.df.copy()
        if gorsel_filter:
            if gorsel_filter.lower() == 'bagimli':
                # Visual dependent
                filtered_df = filtered_df[
                    filtered_df['gorsel_bagimli'].astype(str).str.lower().str.contains('bagimli|var', na=False)
                ]
            elif gorsel_filter.lower() == 'bagimsiz':
                # Visual independent
                filtered_df = filtered_df[
                    filtered_df['gorsel_bagimli'].astype(str).str.lower().str.contains('bagimsiz|yok|hayir', na=False)
                ]
            elif gorsel_filter.lower() == 'destekleyici':
                # Supporting visual
                filtered_df = filtered_df[
                    filtered_df['gorsel_bagimli'].astype(str).str.lower().str.contains('destekleyici', na=False)
                ]
            
            if len(filtered_df) == 0:
                # No questions match filter, return None
                return None
        
        # Select random row from filtered dataset
        random_idx = random.randint(0, len(filtered_df) - 1)
        row = filtered_df.iloc[random_idx]
        
        # Build options dict
        options = {}
        for opt in ['A', 'B', 'C', 'D', 'E']:
            col_name = f'secenek_{opt}'
            if col_name in row and pd.notna(row[col_name]):
                options[opt] = str(row[col_name]).strip()
        
        # Get correct answer
        correct_answer = None
        if 'dogru_cevap' in row and pd.notna(row['dogru_cevap']):
            correct_answer = str(row['dogru_cevap']).strip().upper()
        
        # Get visual dependency
        gorsel_bagimli = None
        if 'gorsel_bagimli' in row and pd.notna(row['gorsel_bagimli']):
            gorsel_bagimli = str(row['gorsel_bagimli']).strip()
        
        return {
            'id': int(row.get('id', random_idx)) if pd.notna(row.get('id')) else random_idx,
            'soru_metin': str(row['soru_metin']).strip(),
            'secenekler': options,
            'dogru_cevap': correct_answer,
            'alt_konu': str(row.get('alt_konu', '')).strip() if pd.notna(row.get('alt_konu')) else None,
            'soru_tipi': str(row.get('soru_tipi', '')).strip() if pd.notna(row.get('soru_tipi')) else None,
            'gorsel_bagimli': gorsel_bagimli,
            'zorluk': str(row.get('zorluk', '')).strip() if pd.notna(row.get('zorluk')) else None
        }


# Singleton instance
_question_generator = None

def get_question_generator(dataset_path: Optional[str] = None) -> QuestionGenerator:
    """Get singleton question generator instance"""
    global _question_generator
    if _question_generator is None:
        _question_generator = QuestionGenerator(dataset_path)
    return _question_generator

