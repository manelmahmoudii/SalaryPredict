"""
Application Flask simplifiée pour la prédiction de salaire
Inclut le modèle ML et l'interface web
"""

from flask import Flask, render_template, request, jsonify
import pandas as pd
import numpy as np
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

app = Flask(__name__)

# Variables globales pour le modèle
model = None
vectorizer = None
location_encoder = None
is_trained = False

def load_data():
    """Charge les données scrapées"""
    data_file = 'data/jobs_data.csv'
    
    if os.path.exists(data_file):
        df = pd.read_csv(data_file, encoding='utf-8')
        # Garder seulement les offres avec salaire
        df_with_salary = df[df['salary'].notna()]
        
        if len(df_with_salary) >= 5:
            print(f"✅ Données scrapées chargées: {len(df_with_salary)} offres avec salaire")
            return df_with_salary
        else:
            print(f"⚠️  Données scrapées trouvées mais peu de salaires ({df['salary'].notna().sum()}/{len(df)})")
            print("   Utilisation de données d'exemple pour l'entraînement.")
    
    # Données d'exemple si pas assez de données scrapées
    print("📝 Utilisation de données d'exemple.")
    return pd.DataFrame([
        {'title': 'Développeur Python', 'location': 'Paris', 'description': 'Python Django Flask', 'salary': 45000},
        {'title': 'Développeur Python Senior', 'location': 'Paris', 'description': 'Python Django Docker', 'salary': 55000},
        {'title': 'Data Scientist', 'location': 'Paris', 'description': 'Machine Learning Python', 'salary': 52000},
        {'title': 'Data Scientist Senior', 'location': 'Paris', 'description': 'ML Deep Learning', 'salary': 65000},
        {'title': 'Ingénieur Logiciel', 'location': 'Lyon', 'description': 'Java Spring', 'salary': 47000},
        {'title': 'Développeur Full Stack', 'location': 'Lyon', 'description': 'React Node.js', 'salary': 46000},
        {'title': 'Développeur Python', 'location': 'Lyon', 'description': 'Flask API', 'salary': 42000},
        {'title': 'Data Scientist', 'location': 'Lyon', 'description': 'Python scikit-learn', 'salary': 48000},
        {'title': 'Ingénieur DevOps', 'location': 'Paris', 'description': 'Docker Kubernetes', 'salary': 50000},
        {'title': 'Architecte Logiciel', 'location': 'Paris', 'description': 'Architecture Cloud', 'salary': 70000},
    ])

def train_model():
    """Entraîne le modèle de prédiction"""
    global model, vectorizer, location_encoder, is_trained
    
    print("\n" + "=" * 60)
    print("🤖 ENTRAÎNEMENT DU MODÈLE")
    print("=" * 60)
    
    # Charger les données
    df = load_data()
    
    if len(df) < 5:
        print("❌ Pas assez de données pour entraîner le modèle")
        return False
    
    print(f"📊 {len(df)} offres chargées")
    
    # Préparer les features
    # 1. TF-IDF sur titre + description
    text_features = df['title'] + ' ' + df['description'].fillna('')
    vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(text_features)
    
    # 2. Encoder la localisation
    location_encoder = LabelEncoder()
    location_encoded = location_encoder.fit_transform(df['location'].fillna('Unknown'))
    
    # 3. Combiner les features
    X_tfidf = pd.DataFrame(tfidf_matrix.toarray())
    X_location = pd.DataFrame({'location': location_encoded})
    X = pd.concat([X_location, X_tfidf], axis=1)
    
    # Convertir tous les noms de colonnes en strings (requis par scikit-learn)
    X.columns = X.columns.astype(str)
    
    y = df['salary'].values
    
    # Entraîner le modèle
    print("🔄 Entraînement en cours...")
    model = RandomForestRegressor(n_estimators=50, random_state=42, max_depth=10)
    model.fit(X, y)
    
    # Évaluation simple
    predictions = model.predict(X)
    mae = np.mean(np.abs(predictions - y))
    
    print(f"✅ Modèle entraîné!")
    print(f"📊 Erreur moyenne: {mae:,.0f} €")
    print(f"💰 Salaire moyen: {y.mean():,.0f} €")
    print("=" * 60)
    
    is_trained = True
    return True

def predict_salary(job_title, location, description=""):
    """Prédit le salaire pour une offre"""
    global model, vectorizer, location_encoder
    
    if not is_trained:
        return None
    
    # Préparer les données
    text = job_title + ' ' + description
    tfidf = vectorizer.transform([text])
    
    # Encoder la localisation
    if location in location_encoder.classes_:
        loc_encoded = location_encoder.transform([location])[0]
    else:
        loc_encoded = 0  # Valeur par défaut
    
    # Combiner features
    X_tfidf = pd.DataFrame(tfidf.toarray())
    X_location = pd.DataFrame({'location': [loc_encoded]})
    X = pd.concat([X_location, X_tfidf], axis=1)
    
    # Convertir tous les noms de colonnes en strings
    X.columns = X.columns.astype(str)
    
    # Prédire
    prediction = model.predict(X)[0]
    return prediction

@app.route('/')
def index():
    """Page d'accueil"""
    return render_template('index.html', trained=is_trained)

@app.route('/predict', methods=['POST'])
def predict():
    """Endpoint de prédiction"""
    try:
        # Récupérer les données
        job_title = request.form.get('job_title', '')
        location = request.form.get('location', '')
        description = request.form.get('description', '')
        
        if not job_title or not location:
            return render_template('index.html', 
                                 trained=is_trained,
                                 error="Veuillez remplir le titre et la localisation")
        
        if not is_trained:
            return render_template('index.html',
                                 trained=is_trained,
                                 error="Modèle non entraîné")
        
        # Prédire
        salary = predict_salary(job_title, location, description)
        
        return render_template('index.html',
                             trained=is_trained,
                             prediction=salary,
                             job_title=job_title,
                             location=location)
    
    except Exception as e:
        return render_template('index.html',
                             trained=is_trained,
                             error=f"Erreur: {str(e)}")

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API JSON pour la prédiction"""
    try:
        data = request.get_json()
        
        job_title = data.get('job_title', '')
        location = data.get('location', '')
        description = data.get('description', '')
        
        if not job_title or not location:
            return jsonify({'success': False, 'error': 'Titre et localisation requis'}), 400
        
        if not is_trained:
            return jsonify({'success': False, 'error': 'Modèle non entraîné'}), 500
        
        salary = predict_salary(job_title, location, description)
        
        return jsonify({
            'success': True,
            'salary': float(salary),
            'salary_formatted': f"{salary:,.0f} €"
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 SALARYPREDICT - VERSION SIMPLE")
    print("=" * 60)
    
    # Entraîner le modèle au démarrage
    train_model()
    
    print(f"\n🌐 Application disponible sur: http://localhost:8080")
    print("=" * 60 + "\n")
    
    app.run(host='0.0.0.0', port=8080, debug=True)

