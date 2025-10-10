"""
Model Training Script for Essay Grading System - Fixed for TSV/CSV format
This script trains models for all 8 essay sets
"""

import pandas as pd
import numpy as np
import pickle
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import cohen_kappa_score, mean_squared_error, mean_absolute_error
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import warnings
warnings.filterwarnings('ignore')

# Download NLTK data
print("Downloading NLTK data...")
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    print("✓ NLTK data downloaded successfully")
except Exception as e:
    print(f"⚠ Warning: {e}")

def load_dataset(data_path):
    """
    Load dataset from various formats (TSV, CSV, XLSX) with robust encoding handling
    """
    print(f"Attempting to load: {data_path}")
    
    # Try different encodings for TSV
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
    
    for encoding in encodings:
        try:
            print(f"Trying TSV with {encoding} encoding...")
            df = pd.read_csv(
                data_path, 
                sep='\t', 
                encoding=encoding,
                quoting=3,  # QUOTE_NONE
                on_bad_lines='skip',
                engine='python'
            )
            print(f"✓ Loaded as TSV with {encoding} encoding: {len(df)} rows")
            return df
        except Exception as e:
            print(f"  Failed with {encoding}: {str(e)[:80]}")
    
    # Try CSV with different encodings
    for encoding in encodings:
        try:
            print(f"Trying CSV with {encoding} encoding...")
            df = pd.read_csv(
                data_path,
                encoding=encoding,
                on_bad_lines='skip',
                engine='python'
            )
            print(f"✓ Loaded as CSV with {encoding} encoding: {len(df)} rows")
            return df
        except Exception as e:
            print(f"  Failed with {encoding}: {str(e)[:80]}")
    
    # Try Excel formats
    try:
        print("Trying Excel format with openpyxl...")
        df = pd.read_excel(data_path, engine='openpyxl')
        print(f"✓ Loaded as Excel with {len(df)} rows")
        return df
    except Exception as e:
        print(f"  Excel (openpyxl) failed: {str(e)[:80]}")
    
    raise ValueError("Could not load dataset in any supported format")

def preprocess_text(text):
    """Clean and preprocess essay text"""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\']', '', text)
    text = ' '.join(text.split())
    return text

def extract_features(essay):
    """Extract comprehensive linguistic features from essay"""
    features = {}
    
    # Tokenization
    words = word_tokenize(essay.lower())
    sentences = sent_tokenize(essay)
    
    # Basic statistics
    features['word_count'] = len(words)
    features['sentence_count'] = len(sentences) if sentences else 1
    features['avg_word_length'] = np.mean([len(word) for word in words]) if words else 0
    features['avg_sentence_length'] = len(words) / len(sentences) if sentences else 0
    features['char_count'] = len(essay)
    
    # Punctuation
    features['punctuation_count'] = sum(1 for c in essay if c in '.,!?;:')
    features['comma_count'] = essay.count(',')
    features['period_count'] = essay.count('.')
    features['exclamation_count'] = essay.count('!')
    features['question_count'] = essay.count('?')
    
    # Vocabulary richness
    unique_words = set(words)
    features['unique_word_count'] = len(unique_words)
    features['unique_word_ratio'] = len(unique_words) / len(words) if words else 0
    
    # Stop words
    stop_words = set(stopwords.words('english'))
    stopword_count = sum(1 for w in words if w.lower() in stop_words)
    features['stopword_count'] = stopword_count
    features['stopword_ratio'] = stopword_count / len(words) if words else 0
    
    # Long words
    features['long_word_count'] = sum(1 for w in words if len(w) > 6)
    features['long_word_ratio'] = features['long_word_count'] / len(words) if words else 0
    
    # POS tagging
    try:
        pos_tags = nltk.pos_tag(words)
        noun_count = sum(1 for _, tag in pos_tags if tag.startswith('NN'))
        verb_count = sum(1 for _, tag in pos_tags if tag.startswith('VB'))
        adj_count = sum(1 for _, tag in pos_tags if tag.startswith('JJ'))
        adv_count = sum(1 for _, tag in pos_tags if tag.startswith('RB'))
        
        features['noun_count'] = noun_count
        features['verb_count'] = verb_count
        features['adj_count'] = adj_count
        features['adv_count'] = adv_count
        features['noun_ratio'] = noun_count / len(words) if words else 0
        features['verb_ratio'] = verb_count / len(words) if words else 0
        features['adj_ratio'] = adj_count / len(words) if words else 0
        features['adv_ratio'] = adv_count / len(words) if words else 0
    except:
        features['noun_count'] = 0
        features['verb_count'] = 0
        features['adj_count'] = 0
        features['adv_count'] = 0
        features['noun_ratio'] = 0
        features['verb_ratio'] = 0
        features['adj_ratio'] = 0
        features['adv_ratio'] = 0
    
    # Sentence length variation
    if sentences:
        sent_lengths = [len(word_tokenize(sent)) for sent in sentences]
        features['sent_length_std'] = np.std(sent_lengths)
        features['sent_length_max'] = max(sent_lengths)
        features['sent_length_min'] = min(sent_lengths)
    else:
        features['sent_length_std'] = 0
        features['sent_length_max'] = 0
        features['sent_length_min'] = 0
    
    return features

def train_essay_set_model(essay_set, data_path='data/training_set_rel3.tsv'):
    """Train model for specific essay set"""
    print(f"\n{'='*60}")
    print(f"Training Model for Essay Set {essay_set}")
    print(f"{'='*60}")
    
    try:
        # Load data
        print(f"Loading data...")
        df = load_dataset(data_path)
        
        # Display available columns
        print(f"Available columns: {df.columns.tolist()}")
        
        # Filter for specific essay set
        # Common column names: essay_set, rater1_domain1, domain1_score, etc.
        if 'essay_set' in df.columns:
            df = df[df['essay_set'] == essay_set]
            print(f"✓ Filtered to essay set {essay_set}: {len(df)} essays")
        else:
            print(f"⚠ Warning: 'essay_set' column not found. Using all data.")
        
        if len(df) == 0:
            raise ValueError(f"No data found for essay set {essay_set}")
        
        # Find essay and score columns
        essay_col = None
        score_col = None
        
        # Look for exact column name first
        if 'essay' in df.columns:
            essay_col = 'essay'
        
        # Look for score column
        if 'domain1_score' in df.columns:
            score_col = 'domain1_score'
        elif 'rater1_domain1' in df.columns:
            score_col = 'rater1_domain1'
        
        if essay_col is None:
            raise ValueError("Could not find essay column")
        if score_col is None:
            raise ValueError("Could not find score column")
        
        print(f"Using essay column: '{essay_col}'")
        print(f"Using score column: '{score_col}'")
        
        # Preprocess essays
        print("Preprocessing essays...")
        df['essay_clean'] = df[essay_col].apply(preprocess_text)
        df = df[df['essay_clean'].str.len() > 0]
        print(f"✓ {len(df)} essays after preprocessing")
        
        # Extract features
        print("Extracting linguistic features...")
        feature_list = []
        for idx, essay in enumerate(df['essay_clean']):
            if idx % 100 == 0:
                print(f"  Processed {idx}/{len(df)} essays...", end='\r')
            feature_list.append(extract_features(essay))
        print(f"✓ Extracted features for {len(feature_list)} essays")
        
        feature_df = pd.DataFrame(feature_list)
        
        # TF-IDF features
        print("Generating TF-IDF features...")
        vectorizer = TfidfVectorizer(
            max_features=500,
            ngram_range=(1, 2),
            min_df=1,  # Changed from 2 to 1
            max_df=1.0,  # Changed from 0.95 to 1.0
            strip_accents='unicode'
        )
        tfidf_features = vectorizer.fit_transform(df['essay_clean'])
        print(f"✓ Generated {tfidf_features.shape[1]} TF-IDF features")
        
        # Combine features
        X = np.hstack([feature_df.values, tfidf_features.toarray()])
        y = df[score_col].values
        
        print(f"\nFeature matrix shape: {X.shape}")
        print(f"Score range: {y.min()} - {y.max()}")
        print(f"Mean score: {y.mean():.2f}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train Gradient Boosting model
        print("\nTraining Gradient Boosting model...")
        model = GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.1,
            max_depth=5,
            min_samples_split=4,
            min_samples_leaf=2,
            subsample=0.8,
            random_state=42,
            verbose=0
        )
        
        model.fit(X_train, y_train)
        print("✓ Model trained successfully")
        
        # Evaluate on test set
        print("\nEvaluating model...")
        y_pred = model.predict(X_test)
        y_pred_rounded = np.round(y_pred)
        y_pred_clipped = np.clip(y_pred_rounded, y.min(), y.max())
        
        # Calculate metrics
        kappa = cohen_kappa_score(y_test, y_pred_clipped, weights='quadratic')
        mse = mean_squared_error(y_test, y_pred_clipped)
        mae = mean_absolute_error(y_test, y_pred_clipped)
        rmse = np.sqrt(mse)
        
        # Accuracy within 1 point
        accuracy_1 = np.mean(np.abs(y_test - y_pred_clipped) <= 1) * 100
        
        print(f"\n{'Performance Metrics':-^60}")
        print(f"Cohen's Kappa (QWK): {kappa:.4f}")
        print(f"Mean Squared Error:  {mse:.4f}")
        print(f"Root MSE:            {rmse:.4f}")
        print(f"Mean Absolute Error: {mae:.4f}")
        print(f"Accuracy (±1 point): {accuracy_1:.2f}%")
        
        # Feature importance
        feature_importance = model.feature_importances_
        top_features_idx = np.argsort(feature_importance)[-10:]
        feature_names = list(feature_df.columns) + [f'tfidf_{i}' for i in range(tfidf_features.shape[1])]
        
        print(f"\n{'Top 10 Important Features':-^60}")
        for idx in reversed(top_features_idx):
            print(f"  {feature_names[idx]}: {feature_importance[idx]:.4f}")
        
        # Create directories if they don't exist
        os.makedirs('models', exist_ok=True)
        os.makedirs('vectorizers', exist_ok=True)
        
        # Save model and vectorizer
        model_path = f'models/model_set{essay_set}.pkl'
        vectorizer_path = f'vectorizers/vectorizer_set{essay_set}.pkl'
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
        
        print(f"\n✓ Model saved to {model_path}")
        print(f"✓ Vectorizer saved to {vectorizer_path}")
        
        return {
            'essay_set': essay_set,
            'kappa': kappa,
            'mse': mse,
            'rmse': rmse,
            'mae': mae,
            'accuracy_1': accuracy_1,
            'samples': len(df)
        }
        
    except Exception as e:
        print(f"\n✗ Error training model for Essay Set {essay_set}: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def find_data_file():
    """Find the training data file in various locations"""
    possible_paths = [
        'data/training_set_rel3.tsv',
        'data/training_set_rel3.csv',
        'data/training_set_rel3.xlsx',
        'data/training_set_rel3.xls',
        'training_set_rel3.tsv',
        'training_set_rel3.csv',
        'training_set_rel3.xlsx',
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"✓ Found data file: {path}")
            return path
    
    return None

def train_all_models():
    """Train models for all essay sets"""
    print("\n" + "="*60)
    print("AUTOMATED ESSAY GRADING SYSTEM - MODEL TRAINING")
    print("="*60)
    
    # Find data file
    data_path = find_data_file()
    if data_path is None:
        print("\n✗ Error: Training data file not found!")
        print("Please ensure one of these files exists in the data/ directory:")
        print("  - training_set_rel3.tsv")
        print("  - training_set_rel3.csv")
        print("  - training_set_rel3.xlsx")
        return
    
    results = []
    
    for essay_set in range(1, 9):
        result = train_essay_set_model(essay_set, data_path)
        if result:
            results.append(result)
    
    # Summary
    if len(results) > 0:
        print("\n" + "="*60)
        print("TRAINING SUMMARY")
        print("="*60)
        print(f"\n{'Set':<6} {'Kappa':<10} {'RMSE':<10} {'MAE':<10} {'Acc±1':<10} {'Samples':<10}")
        print("-" * 60)
        
        for result in results:
            print(f"{result['essay_set']:<6} "
                  f"{result['kappa']:<10.4f} "
                  f"{result['rmse']:<10.4f} "
                  f"{result['mae']:<10.4f} "
                  f"{result['accuracy_1']:<10.2f} "
                  f"{result['samples']:<10}")
        
        avg_kappa = np.mean([r['kappa'] for r in results])
        avg_rmse = np.mean([r['rmse'] for r in results])
        avg_acc = np.mean([r['accuracy_1'] for r in results])
        
        print("-" * 60)
        print(f"{'AVG':<6} {avg_kappa:<10.4f} {avg_rmse:<10.4f} {'':10} {avg_acc:<10.2f}")
        print(f"\n✓ Successfully trained {len(results)} models!")
        print(f"✓ Average Cohen's Kappa: {avg_kappa:.4f}")
        print(f"✓ Average Accuracy (±1): {avg_acc:.2f}%")
    else:
        print("\n✗ No models were trained successfully")
        print("Please check the error messages above")

if __name__ == "__main__":
    train_all_models()