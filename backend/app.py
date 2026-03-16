import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import numpy as np
import pickle
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import warnings

warnings.filterwarnings('ignore')

# Resolve paths relative to this file (works on Render/gunicorn too)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
VECTORIZERS_DIR = os.path.join(BASE_DIR, 'vectorizers')

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

app = Flask(__name__)
CORS(app)

# Global variables for models
models = {}
vectorizers = {}

def extract_features(essay):
    """Extract comprehensive linguistic features from essay - matches training script exactly"""
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

def preprocess_text(text):
    """Clean and preprocess essay text"""
    # Convert to lowercase
    text = text.lower()
    # Remove special characters but keep punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?;:\']', '', text)
    # Remove extra whitespace
    text = ' '.join(text.split())
    return text

def load_models():
    """Load all pre-trained models"""
    print("Loading models...")
    loaded_count = 0
    
    for essay_set in range(1, 9):
        try:
            model_path = os.path.join(MODELS_DIR, f'model_set{essay_set}.pkl')
            vectorizer_path = os.path.join(VECTORIZERS_DIR, f'vectorizer_set{essay_set}.pkl')
            
            with open(model_path, 'rb') as f:
                models[essay_set] = pickle.load(f)
            with open(vectorizer_path, 'rb') as f:
                vectorizers[essay_set] = pickle.load(f)
            print(f"✓ Loaded model for essay set {essay_set}")
            loaded_count += 1
        except FileNotFoundError:
            print(f"✗ Model for essay set {essay_set} not found")
            print(f"  Expected: {model_path}")
        except Exception as e:
            print(f"✗ Error loading model for essay set {essay_set}: {e}")
    
    if loaded_count == 0:
        print("\n⚠ WARNING: No models loaded!")
        print("Please run: python train_models.py")
    else:
        print(f"\n✓ Successfully loaded {loaded_count}/8 models")

@app.route('/api/grade', methods=['POST'])
def grade_essay():
    """Grade an essay"""
    try:
        data = request.json
        essay = data.get('essay', '')
        essay_set = int(data.get('essay_set', 1))
        
        if not essay or essay_set not in range(1, 9):
            return jsonify({'error': 'Invalid input'}), 400
        
        # Check if model exists
        if essay_set not in models or essay_set not in vectorizers:
            return jsonify({
                'error': f'Model for essay set {essay_set} not loaded',
                'hint': 'Deploy the trained .pkl files to backend/models and backend/vectorizers, then redeploy the backend.'
            }), 503
        
        # Preprocess essay
        processed_essay = preprocess_text(essay)
        
        # Extract features
        features = extract_features(processed_essay)
        feature_array = np.array(list(features.values())).reshape(1, -1)
        
        # TF-IDF features
        tfidf_features = vectorizers[essay_set].transform([processed_essay])
        
        # Combine features
        X = np.hstack([feature_array, tfidf_features.toarray()])
        
        # Predict score
        score = models[essay_set].predict(X)[0]
        score = np.clip(np.round(score), 0, get_max_score(essay_set))
        
        # Generate feedback
        feedback = generate_feedback(features, score, essay_set)
        
        return jsonify({
            'score': int(score),
            'maxScore': get_max_score(essay_set),
            'features': features,
            'feedback': feedback
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_max_score(essay_set):
    """Get maximum score for essay set"""
    max_scores = {1: 12, 2: 6, 3: 3, 4: 3, 5: 4, 6: 4, 7: 30, 8: 60}
    return max_scores.get(essay_set, 10)

def generate_feedback(features, score, essay_set):
    """Generate feedback based on features"""
    strengths = []
    improvements = []
    
    max_score = get_max_score(essay_set)
    score_percentage = (score / max_score) * 100
    
    # Word count feedback
    if features['word_count'] > 300:
        strengths.append("Excellent essay length with detailed content")
    elif features['word_count'] > 200:
        strengths.append("Good essay length")
    else:
        improvements.append("Consider expanding your ideas with more details")
    
    # Vocabulary feedback
    if features['unique_word_ratio'] > 0.6:
        strengths.append("Rich and diverse vocabulary usage")
    elif features['unique_word_ratio'] < 0.4:
        improvements.append("Try using more varied vocabulary")
    
    # Sentence structure
    if features['avg_sentence_length'] > 15 and features['avg_sentence_length'] < 25:
        strengths.append("Well-balanced sentence structure")
    elif features['avg_sentence_length'] < 10:
        improvements.append("Use more complex sentence structures")
    elif features['avg_sentence_length'] > 30:
        improvements.append("Break down long sentences for better readability")
    
    # Organization
    if features['sentence_count'] > 10:
        strengths.append("Well-organized with multiple paragraphs")
    else:
        improvements.append("Add more supporting sentences and paragraphs")
    
    # Grammar (using noun/verb ratio as proxy)
    if features['noun_ratio'] > 0.2 and features['verb_ratio'] > 0.1:
        strengths.append("Good balance of descriptive and action words")
    
    return {
        'strengths': strengths,
        'improvements': improvements,
        'vocabulary': 'Advanced' if features['unique_word_ratio'] > 0.6 else 'Good' if features['unique_word_ratio'] > 0.45 else 'Basic'
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    missing_models = [s for s in range(1, 9) if s not in models or s not in vectorizers]
    return jsonify({
        'status': 'healthy',
        'models_loaded': len(models),
        'missing_essay_sets': missing_models
    })

# Load models at module level (works for both gunicorn and direct run)
load_models()

if __name__ == '__main__':
    print("\nStarting Flask server...")
    port = int(os.environ.get('PORT', 5000))
    print(f"Backend running at: http://0.0.0.0:{port}")
    print("\nPress CTRL+C to quit\n")
    app.run(debug=True, host='0.0.0.0', port=port)