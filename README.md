# 💰 SalaryPredict - Prédiction de Salaire avec IA

Une application web moderne qui prédit les salaires en temps réel en analysant les offres d'emploi sur Indeed.

## ✨ Fonctionnalités Principales

- **🔍 Scraping en Temps Réel** : Collecte les offres d'emploi sur Indeed au moment de la recherche.
- **🤖 Intelligence Artificielle** : Modèle de Machine Learning (Random Forest) pour estimer les salaires.
- **🎨 Interface Moderne** : Design épuré avec Tailwind CSS, animations fluides et responsive.
- **🌙 Mode Sombre** : Support complet du thème sombre (Dark Mode) avec bascule automatique.
- **⚡ Expérience Utilisateur** : Feedback visuel immédiat, indicateurs de chargement et gestion des erreurs.

## �️ Technologies Utilisées

- **Backend** : Python, Flask
- **Scraping** : Selenium, BeautifulSoup
- **Machine Learning** : scikit-learn, pandas, numpy
- **Frontend** : HTML5, Tailwind CSS, JavaScript

## � Installation

1. **Cloner le projet** (ou télécharger les fichiers)

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prérequis Système**
   - Avoir Google Chrome installé (pour Selenium)
   - Python 3.8 ou supérieur

## 📖 Utilisation

1. **Lancer l'application**
   ```bash
   python app.py
   ```

2. **Accéder à l'interface**
   - Ouvrez votre navigateur sur : `http://localhost:8080`

3. **Faire une prédiction**
   - Entrez un **titre de poste** (ex: "Data Scientist")
   - Entrez une **localisation** (ex: "Paris")
   - Cliquez sur **"Scraper Indeed et Prédire"**

## 📂 Structure du Projet

```
Project Python SalaryPredict/
├── app.py                 # Application principale Flask + Logique ML
├── scraper.py             # Script de scraping Selenium
├── requirements.txt       # Liste des dépendances Python
├── README.md              # Documentation du projet
└── templates/
    └── index.html         # Interface utilisateur (HTML/Tailwind)
```

## 🧠 Comment ça marche ?

1. **L'utilisateur** lance une recherche depuis l'interface web.
2. **Le Scraper** (Selenium) lance un navigateur invisible, va sur Indeed et récupère les dernières offres correspondantes.
3. **L'Analyseur** vérifie si des offres ont été trouvées :
   - *Si 0 offre* : Affiche un avertissement avec des conseils.
   - *Si offres trouvées* : Extrait les données (entreprises, descriptions...).
4. **Le Modèle ML** utilise les caractéristiques du poste (mots-clés, ville) pour prédire une fourchette de salaire.
5. **Le Résultat** est affiché instantanément avec le salaire estimé et les détails des offres trouvées.

## ⚠️ Notes Importantes

- **Temps de chargement** : Le scraping prend environ 10-15 secondes car il navigue réellement sur le web.
- **Données manquantes** : Si Indeed ne retourne aucun résultat, l'application vous avertira et vous suggérera d'élargir votre recherche.
- **Précision** : La prédiction est une estimation basée sur un modèle statistique et peut varier par rapport à la réalité.

---
*Projet réalisé dans le cadre d'un cours de Python / Data Science.*
