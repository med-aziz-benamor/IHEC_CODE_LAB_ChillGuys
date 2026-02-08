# 🏦 BVMT Intelligent Trading Assistant

<div align="center">

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.54-FF4B4B.svg)
![Plotly](https://img.shields.io/badge/Plotly-6.5-3F4F75.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)

<h3>🇹🇳 Un Assistant de Trading Intelligent pour le Marché Boursier Tunisien</h3>

*Développé lors du Hackathon IHEC CODELAB 2.0 - Février 2026*

<br>

[🚀 Démarrage Rapide](#-démarrage-rapide) •
[✨ Fonctionnalités](#-fonctionnalités) •
[🏗 Architecture](#-architecture) •
[📚 Documentation](#-documentation-des-modules) •
[👥 Équipe](#-équipe)

<br>

<img src="https://img.shields.io/badge/Valeurs%20Analysées-598-blue?style=for-the-badge" />
<img src="https://img.shields.io/badge/Données-144K+%20lignes-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/Modules-6%20intégrés-green?style=for-the-badge" />

</div>

---

## 📋 Table des Matières

1. [Aperçu du Projet](#-aperçu-du-projet)
2. [Fonctionnalités](#-fonctionnalités)
3. [Démarrage Rapide](#-démarrage-rapide)
4. [Architecture Technique](#-architecture)
5. [Documentation des Modules](#-documentation-des-modules)
   - [Data Loader](#1-data-loader-modulesshareddataloaderpy)
   - [Forecasting](#2-forecasting-modulesforecastingpredictpy)
   - [Sentiment Analysis](#3-sentiment-analysis-modulessentimentanalyzerpy)
   - [Anomaly Detection](#4-anomaly-detection-modulesanomalydetectorpy)
   - [Decision Engine](#5-decision-engine-modulesdecisionenginepy)
   - [Portfolio Manager](#6-portfolio-manager-modulesdecisionportfoliopy)
6. [Dashboard Streamlit](#-dashboard-streamlit)
7. [API REST](#-api-rest)
8. [Structure du Projet](#-structure-du-projet)
9. [Données BVMT](#-données-bvmt)
10. [Tests](#-tests)
11. [Équipe](#-équipe)
12. [Améliorations Futures](#-améliorations-futures)

---

## 🎯 Aperçu du Projet

Le **BVMT Intelligent Trading Assistant** est une plateforme complète d'aide à la décision d'investissement pour la Bourse des Valeurs Mobilières de Tunis. Notre système combine **quatre modules d'analyse avancés** pour générer des recommandations d'achat, de vente ou de conservation avec des **explications détaillées en français**.

### 🌟 Proposition de Valeur

| Problème | Notre Solution |
|----------|----------------|
| Analyse manuelle chronophage | ⚡ Analyse automatisée de 100+ valeurs |
| Décisions basées sur l'émotion | 🧠 Recommandations basées sur les données |
| Manque de transparence | 💡 Explications détaillées pour chaque décision |
| Surveillance impossible 24/7 | ⚠️ Détection automatique des anomalies |
| Difficulté à suivre les performances | 📊 Dashboard interactif avec métriques |

### 🎯 Objectifs du Système

```
┌─────────────────────────────────────────────────────────────────────┐
│  📈 PRÉVISION      │  Anticiper les mouvements de prix à 5 jours    │
├────────────────────┼────────────────────────────────────────────────┤
│  📰 SENTIMENT      │  Évaluer l'opinion via les actualités          │
├────────────────────┼────────────────────────────────────────────────┤
│  ⚠️ ANOMALIES      │  Détecter les comportements suspects           │
├────────────────────┼────────────────────────────────────────────────┤
│  💡 DÉCISION       │  Générer des recommandations explicables       │
├────────────────────┼────────────────────────────────────────────────┤
│  💼 PORTEFEUILLE   │  Simuler et suivre les performances            │
└────────────────────┴────────────────────────────────────────────────┘
```

---

## ✨ Fonctionnalités

### 📊 Page 1: Vue d'Ensemble du Marché

<table>
<tr>
<td width="50%">

**Indicateurs Clés**
- 📈 Tendance générale (Haussier/Baissier/Neutre)
- 📊 Nombre de valeurs analysées
- ⚠️ Alertes actives
- 💰 Valeur du portefeuille

</td>
<td width="50%">

**Recommandations**
- 🟢 Top 5 opportunités d'achat
- 🔴 Top 5 alertes de vente
- 📉 Distribution des signaux
- 🔔 Feed d'alertes en temps réel

</td>
</tr>
</table>

### 🔍 Page 2: Analyse Approfondie par Valeur

**4 onglets d'analyse :**

| Onglet | Contenu |
|--------|---------|
| 📈 **Prévision** | Graphique historique + prévisions 5 jours, métriques du modèle (RMSE, MAE), analyse de tendance |
| 📰 **Sentiment** | Jauge de sentiment (-1 à +1), articles analysés, résumé automatique |
| ⚠️ **Anomalies** | Score de risque (0-10), liste des anomalies détectées, timeline visuelle |
| 💡 **Recommandation** | BUY/SELL/HOLD avec confiance, **bouton "Pourquoi?"** avec explication détaillée |

### 💼 Page 3: Gestion de Portefeuille

- 💵 **Capital initial** : 10,000 TND (configurable)
- 📊 **Métriques** : ROI, gain/perte, taux de succès
- 📋 **Positions** : Tableau avec P&L par position
- 🥧 **Allocation** : Graphique circulaire interactif
- 📜 **Historique** : Toutes les transactions

### ⚠️ Page 4: Système d'Alertes

- 🔴 **Alertes critiques** : Anomalies sévères
- 🟡 **Alertes modérées** : Comportements inhabituels
- 🟢 **Informations** : Mises à jour générales
- 🔄 **Scan du marché** : Bouton pour analyse complète

---

## 🚀 Démarrage Rapide

### Prérequis

```
✅ Python 3.9 ou supérieur
✅ pip (gestionnaire de packages)
✅ 500 Mo d'espace disque
✅ Connexion internet (pour installation)
```

### Installation en 4 Étapes

```bash
# 1️⃣ Cloner le repository
git clone https://github.com/votre-repo/bvmt-trading-assistant.git
cd bvmt-trading-assistant

# 2️⃣ Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# Windows: venv\Scripts\activate

# 3️⃣ Installer les dépendances
pip install -r requirements.txt

# 4️⃣ Vérifier l'installation
python -m tests.test_integration
```

### Lancement du Dashboard

```bash
# Activer l'environnement
source venv/bin/activate

# Lancer Streamlit
streamlit run dashboard/app.py
```

🌐 **Accès** : http://localhost:8501

### Lancement de l'API REST

```bash
# Dans un terminal séparé
source venv/bin/activate
python api.py
```

🔌 **API** : http://localhost:5000

### 🧠 Market Memory (Optional - Added Value)

Our system includes a **semantic intelligence layer** using Qdrant vector database for explainable AI and evidence retrieval.

```bash
# 1️⃣ Install Market Memory dependencies
pip install qdrant-client sentence-transformers scikit-learn

# 2️⃣ Start Qdrant container
docker compose up -d qdrant

# 3️⃣ Ingest data into Market Memory (~30 seconds)
python scripts/ingest_memory.py --limit 100

# 4️⃣ Verify in dashboard
# Look for "🧠 Market Memory: ✅ Actif" in sidebar
```

**📚 Full Guide**: See [MARKET_MEMORY_GUIDE.md](MARKET_MEMORY_GUIDE.md) for complete documentation.

**What it adds**:
- 🔎 **Semantic search** across news, anomalies, and recommendations
- 🔗 **Pattern matching** to find similar historical events
- 💡 **Evidence-based explanations** with retrieved context
- ⚡ **Fast** sub-second searches with similarity scores

**Works offline**: Once the model is downloaded, no internet required for demo!

---

## 🏗 Architecture

### Vue d'Ensemble

```
┌─────────────────────────────────────────────────────────────────────┐
│                      🖥️  DASHBOARD STREAMLIT                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐     │
│  │ Vue d'Ens.   │ Analyse Val. │ Portefeuille │   Alertes    │     │
│  └──────────────┴──────────────┴──────────────┴──────────────┘     │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      🧠  DECISION ENGINE                             │
│                                                                      │
│   ┌────────────────────────────────────────────────────────────┐   │
│   │  Agrégation des Signaux  →  Score (-10 à +10)  →  BUY/SELL │   │
│   │           +                                                 │   │
│   │  Génération d'Explications en Français                     │   │
│   └────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                    │              │              │
         ┌──────────┘              │              └──────────┐
         ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  📈 FORECASTING │    │  📰 SENTIMENT   │    │  ⚠️ ANOMALY     │
│    (40% poids)  │    │    (30% poids)  │    │    (20% poids)  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Prophet/MA    │    │ • Mots-clés FR  │    │ • Volume spike  │
│ • Trend 5 jours │    │ • Score -1 à +1 │    │ • Price gap     │
│ • RMSE, MAE     │    │ • Headlines     │    │ • Volatilité    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                         │                         │
         └─────────────────────────┼─────────────────────────┘
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      📁  DATA LOADER                                 │
│                                                                      │
│   CSV BVMT  →  Nettoyage  →  Standardisation  →  Cache Mémoire     │
│                                                                      │
│   📊 598 valeurs  •  144,000+ lignes  •  Données 2022               │
└─────────────────────────────────────────────────────────────────────┘
```

### Flux de Décision

```
                        CALCUL DU SCORE
                    ━━━━━━━━━━━━━━━━━━━━━

    ┌──────────────┐
    │   FORECAST   │────▶ Trend > +2%  ────▶ +1 à +4 points
    │   (40%)      │────▶ Trend < -2%  ────▶ -1 à -4 points
    └──────────────┘

    ┌──────────────┐
    │  SENTIMENT   │────▶ Score > +0.4 ────▶ +1 à +3 points
    │   (30%)      │────▶ Score < -0.4 ────▶ -1 à -3 points
    └──────────────┘

    ┌──────────────┐
    │   ANOMALY    │────▶ Volume spike ────▶ -2 points
    │   (20%)      │────▶ Price spike  ────▶ -1 point
    └──────────────┘────▶ Normal       ────▶ +1 point

    ┌──────────────┐
    │  TECHNICAL   │────▶ RSI < 30     ────▶ +1.5 points
    │   (10%)      │────▶ RSI > 70     ────▶ -1.5 points
    └──────────────┘


                    DÉCISION FINALE
                ━━━━━━━━━━━━━━━━━━━━━━

              Score ≥ +3  ────▶  🟢 BUY
              Score ≤ -3  ────▶  🔴 SELL
              Sinon       ────▶  🟡 HOLD
```

### Profils Utilisateur

| Profil | Multiplicateur | Seuil BUY | Seuil SELL | Description |
|--------|---------------|-----------|------------|-------------|
| 🛡️ Conservateur | 0.5x | ≥4.0 | ≤-4.0 | Minimise le risque |
| ⚖️ Modéré | 1.0x | ≥3.0 | ≤-3.0 | Équilibre risque/rendement |
| 🚀 Agressif | 1.2x | ≥2.0 | ≤-2.0 | Maximise les opportunités |

---

## 📚 Documentation des Modules

### 1. Data Loader (`modules/shared/data_loader.py`)

> **Fondation du système** - Chargement et nettoyage des données BVMT

#### Fonctions Principales

```python
from modules.shared.data_loader import (
    load_full_dataset,    # Charger toutes les données
    get_stock_data,       # Données d'une valeur
    get_liquid_stocks,    # Valeurs liquides
    get_current_price,    # Prix actuel
    get_stock_name,       # Nom de la valeur
    get_stock_summary,    # Résumé statistique
)

# Exemple
df = get_stock_data('TN0001600154')  # ATTIJARI BANK
print(f"Lignes: {len(df)}, Prix actuel: {get_current_price('TN0001600154')} TND")
```

#### Schéma des Données

| Colonne | Type | Description | Exemple |
|---------|------|-------------|---------|
| `date` | datetime | Date de séance | 2022-01-03 |
| `stock_code` | str | Code ISIN | TN0001600154 |
| `stock_name` | str | Nom complet | ATTIJARI BANK |
| `open` | float | Prix ouverture | 51.50 |
| `close` | float | Prix clôture | 51.40 |
| `high` | float | Plus haut | 51.90 |
| `low` | float | Plus bas | 50.75 |
| `volume` | int | Quantité | 12,450 |
| `num_transactions` | int | Nb transactions | 28 |

---

### 2. Forecasting (`modules/forecasting/predict.py`)

> **Prévision des prix** - Modèles Prophet et Moving Average

#### Utilisation

```python
from modules.forecasting.predict import predict_next_days, get_trend_analysis

# Prévision à 5 jours
forecast = predict_next_days('TN0001600154', n_days=5)

print(f"Modèle: {forecast['model_used']}")
print(f"RMSE: {forecast['metrics']['rmse']:.2f} TND")

for pred in forecast['predictions']:
    print(f"  {pred['date']}: {pred['predicted_close']:.2f} TND ({pred['confidence']:.0%})")
```

#### Sortie

```python
{
    'stock_code': 'TN0001600154',
    'stock_name': 'ATTIJARI BANK',
    'predictions': [
        {'date': '2026-02-09', 'predicted_close': 52.10, 'confidence': 0.82},
        {'date': '2026-02-10', 'predicted_close': 52.45, 'confidence': 0.80},
        # ...
    ],
    'model_used': 'prophet',  # ou 'simple_ma'
    'metrics': {
        'rmse': 0.45,
        'mae': 0.32,
        'directional_accuracy': 0.65
    }
}
```

#### Modèles Disponibles

| Modèle | Condition | Caractéristiques |
|--------|-----------|------------------|
| **Prophet** | ≥60 jours de données | Saisonnalité, tendances, jours fériés |
| **Simple MA** | Fallback | Moyenne mobile + extrapolation linéaire |

---

### 3. Sentiment Analysis (`modules/sentiment/analyzer.py`)

> **Analyse de sentiment** - NLP français sur les actualités financières

#### Utilisation

```python
from modules.sentiment.analyzer import get_sentiment_score, get_market_sentiment

# Sentiment d'une valeur
result = get_sentiment_score('TN0001600154')

print(f"Score: {result['sentiment_score']:.2f}")  # -1 à +1
print(f"Articles: {result['num_articles']}")
print(f"Résumé: {result['summary']}")
```

#### Sortie

```python
{
    'stock_code': 'TN0001600154',
    'stock_name': 'ATTIJARI BANK',
    'sentiment_score': 0.65,      # -1 (très négatif) à +1 (très positif)
    'confidence': 0.72,
    'num_articles': 5,
    'sample_headlines': [
        {
            'headline': 'Attijari Bank annonce des résultats solides',
            'source': 'Kapitalis',
            'date': '2026-02-05',
            'sentiment': 0.85
        }
    ],
    'summary': 'Sentiment global très positif (0.65)...'
}
```

#### Mots-Clés Analysés

| 🟢 Positifs | 🔴 Négatifs | ⚪ Neutres |
|-------------|-------------|------------|
| croissance, hausse, profit | perte, baisse, crise | maintient, stabilité |
| succès, expansion | dette, risque | prudente, modérée |
| innovation, partenariat | restructuration | stratégie, prévue |

---

### 4. Anomaly Detection (`modules/anomaly/detector.py`)

> **Détection d'anomalies** - Identification des comportements suspects

#### Utilisation

```python
from modules.anomaly.detector import detect_anomalies

result = detect_anomalies('TN0001600154', lookback_days=30)

print(f"Niveau de risque: {result['risk_level']}")
print(f"Score: {result['score']}/10")
print(f"Anomalies: {len(result['anomalies_detected'])}")
```

#### Sortie

```python
{
    'stock_code': 'TN0001600154',
    'stock_name': 'ATTIJARI BANK',
    'risk_level': 'ELEVATED',     # NORMAL, ELEVATED, HIGH
    'score': 4.5,                 # 0-10
    'anomalies_detected': [
        {
            'type': 'volume_spike',
            'severity': 'HIGH',
            'date': '2026-02-03',
            'description': 'Volume 5.2σ au-dessus de la moyenne',
            'metrics': {
                'actual_value': 125000,
                'expected_value': 15000,
                'deviation_sigma': 5.2
            }
        }
    ],
    'summary': 'Anomalies détectées: 1 spike(s) de volume...'
}
```

#### Types d'Anomalies

| Type | Seuil | Sévérité | Description |
|------|-------|----------|-------------|
| **Volume Spike** | >3σ | HIGH/MEDIUM/LOW | Volume anormalement élevé |
| **Price Gap** | >5% | HIGH si >10% | Variation brutale du prix |
| **Low Liquidity** | <5 tx | MEDIUM | Très peu de transactions |
| **High Volatility** | >15% range | HIGH si >20% | Volatilité excessive |

---

### 5. Decision Engine (`modules/decision/engine.py`)

> **Moteur de décision** - Agrégation des signaux et recommandations

#### Utilisation

```python
from modules.decision.engine import make_recommendation, get_top_recommendations

# Recommandation individuelle
rec = make_recommendation('TN0001600154', user_profile='moderate')

print(f"Recommandation: {rec['recommendation']}")  # BUY, SELL, HOLD
print(f"Confiance: {rec['confidence']:.0%}")
print(f"Score: {rec['score']}/10")
```

#### Sortie Complète

```python
{
    'stock_code': 'TN0001600154',
    'stock_name': 'ATTIJARI BANK',
    'current_price': 51.50,
    'recommendation': 'BUY',
    'confidence': 0.85,
    'score': 7.2,
    'risk_level': 'LOW',
    'signals': {
        'forecast': {
            'direction': 'up',
            'magnitude': 0.032,
            'confidence': 0.85,
            'weight': 0.4
        },
        'sentiment': {
            'score': 0.65,
            'num_articles': 5,
            'weight': 0.3
        },
        'anomaly': {
            'detected': False,
            'score': 0.1,
            'weight': 0.2
        },
        'technical': {
            'rsi': 45,
            'signal': 'neutral',
            'weight': 0.1
        }
    },
    'explanation': '... explication détaillée en français ...',
    'suggested_action': 'Acheter 50-100 actions au prix actuel de 51.50 TND',
    'timestamp': '2026-02-08T14:32:00'
}
```

---

### 6. Portfolio Manager (`modules/decision/portfolio.py`)

> **Gestionnaire de portefeuille** - Simulation de trading virtuel

#### Utilisation

```python
from modules.decision.portfolio import Portfolio

# Créer un portefeuille
portfolio = Portfolio(initial_capital=10000.0, name="Mon Portefeuille")

# Acheter
result = portfolio.buy(
    stock_code='TN0001600154',
    stock_name='ATTIJARI BANK',
    price=51.50,
    quantity=50,
    date='2026-02-08'
)
print(result['message'])  # "Achat réussi: 50 actions..."

# Vendre
result = portfolio.sell(
    stock_code='TN0001600154',
    price=53.00,
    quantity=25,
    date='2026-02-10'
)
print(f"P/L: {result['profit_loss']:+.2f} TND")

# Métriques de performance
current_prices = {'TN0001600154': 53.00}
metrics = portfolio.get_performance_metrics(current_prices)
print(f"ROI: {metrics['roi_percentage']:+.2f}%")
print(f"Win Rate: {metrics['win_rate']:.0f}%")
```

#### Méthodes Disponibles

| Méthode | Description |
|---------|-------------|
| `buy()` | Exécuter un ordre d'achat |
| `sell()` | Exécuter un ordre de vente |
| `get_performance_metrics()` | ROI, gain/perte, win rate |
| `get_allocation()` | Allocation en % par position |
| `get_position_details()` | Détails de chaque position |
| `get_transaction_history()` | Historique des transactions |
| `save_to_file()` / `load_from_file()` | Persistance JSON |

---

## 🖥 Dashboard Streamlit

### Captures d'Écran Conceptuelles

```
┌─────────────────────────────────────────────────────────────────────┐
│  🏦 BVMT Trading Assistant                                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │ TUNINDEX │  │ VALEURS  │  │ ALERTES  │  │ PORTFOLIO│           │
│  │  HAUSSIER│  │   107    │  │    3     │  │ 10,450   │           │
│  │   +0.8%  │  │ analysées│  │  actives │  │   TND    │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│                                                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────┐         │
│  │ 🟢 TOP ACHATS           │  │ 🔴 ALERTES VENTE        │         │
│  │                         │  │                         │         │
│  │ ATTIJARI BANK  BUY 85%  │  │ STB          SELL 80%  │         │
│  │ BH BANK        BUY 78%  │  │ TUNISAIR     SELL 75%  │         │
│  │ POULINA        BUY 72%  │  │ ...                    │         │
│  └─────────────────────────┘  └─────────────────────────┘         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Caractéristiques Techniques

| Aspect | Détail |
|--------|--------|
| **Framework** | Streamlit 1.54 |
| **Graphiques** | Plotly (interactifs, zoomables) |
| **Cache** | 5 minutes (performance) |
| **Session** | State persistant |
| **Responsive** | Adapté laptop/tablette |
| **Langue** | Français |

### Lancement

```bash
# Standard
streamlit run dashboard/app.py

# Port personnalisé
streamlit run dashboard/app.py --server.port 8502

# Mode headless (serveur)
streamlit run dashboard/app.py --server.headless true
```

---

## 🔌 API REST

### Endpoints Disponibles

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/api/stocks` | Liste toutes les valeurs |
| `GET` | `/api/stock/<code>` | Info d'une valeur |
| `GET` | `/api/recommend/<code>` | Recommandation |
| `GET` | `/api/market/summary` | Résumé du marché |
| `GET` | `/api/market/top-buys` | Top achats |
| `GET` | `/api/market/top-sells` | Top ventes |
| `GET` | `/api/portfolio` | État du portefeuille |
| `GET` | `/api/portfolio/positions` | Positions ouvertes |
| `GET` | `/api/portfolio/transactions` | Historique |
| `POST` | `/api/portfolio/buy` | Exécuter achat |
| `POST` | `/api/portfolio/sell` | Exécuter vente |
| `POST` | `/api/portfolio/reset` | Réinitialiser |

### Exemples cURL

```bash
# Liste des valeurs
curl http://localhost:5000/api/stocks

# Recommandation avec profil
curl "http://localhost:5000/api/recommend/TN0001600154?profile=moderate"

# Résumé du marché
curl http://localhost:5000/api/market/summary

# Acheter des actions
curl -X POST http://localhost:5000/api/portfolio/buy \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "TN0001600154", "quantity": 50}'

# Vendre des actions
curl -X POST http://localhost:5000/api/portfolio/sell \
  -H "Content-Type: application/json" \
  -d '{"stock_code": "TN0001600154", "quantity": 25}'
```

---

## 📁 Structure du Projet

```
bvmt-trading-assistant/
│
├── 📂 dashboard/
│   └── 🎨 app.py                    # Dashboard Streamlit (1,627 lignes)
│
├── 📂 modules/
│   │
│   ├── 📂 shared/
│   │   └── 📊 data_loader.py        # Chargement données BVMT
│   │
│   ├── 📂 forecasting/
│   │   ├── __init__.py
│   │   └── 📈 predict.py            # Prévision Prophet/MA
│   │
│   ├── 📂 sentiment/
│   │   ├── __init__.py
│   │   └── 📰 analyzer.py           # Analyse sentiment FR
│   │
│   ├── 📂 anomaly/
│   │   ├── __init__.py
│   │   └── ⚠️ detector.py           # Détection anomalies
│   │
│   └── 📂 decision/
│       ├── __init__.py
│       ├── 🧠 engine.py             # Moteur de décision
│       ├── 💼 portfolio.py          # Gestionnaire portefeuille
│       ├── 💡 explainer.py          # Générateur explications
│       ├── 🎭 mocks.py              # Données simulées
│       └── 📊 stock_data.py         # Utilitaires
│
├── 📂 data/
│   ├── 📄 web_histo_cotation_2022.csv
│   ├── 📄 histo_cotation_2023.csv
│   ├── 📄 histo_cotation_2024.csv
│   ├── 📄 histo_cotation_2025.csv
│   └── 📂 sentiment/
│       └── 📄 news_cache.json       # Cache actualités
│
├── 📂 tests/
│   ├── __init__.py
│   └── 🧪 test_integration.py       # Tests d'intégration
│
├── 🔌 api.py                        # API REST Flask
├── 🎮 demo.py                       # Script démo
├── 📋 requirements.txt              # Dépendances
├── 📖 README.md                     # Ce fichier
└── 📘 INTEGRATION_GUIDE.md          # Guide d'intégration
```

---

## 📊 Données BVMT

### Source

Les données proviennent de la **Bourse des Valeurs Mobilières de Tunis (BVMT)**.

### Statistiques du Dataset

| Métrique | Valeur |
|----------|--------|
| **Fichiers** | 4 années (2022-2025) |
| **Lignes totales** | 144,000+ |
| **Valeurs uniques** | 598 codes ISIN |
| **Valeurs liquides** | 107 (volume > 100/jour) |
| **Période principale** | 2022 (données complètes) |

### Top Valeurs Analysées

| Code ISIN | Nom | Secteur |
|-----------|-----|---------|
| TN0001600154 | ATTIJARI BANK | Banque |
| TN0001800457 | BIAT | Banque |
| TN0001900604 | BH BANK | Banque |
| TN0003400058 | AMEN BANK | Banque |
| TN0005700018 | POULINA GP HOLDING | Conglomérat |
| TN0001100254 | SFBT | Agroalimentaire |
| TN0001000108 | MONOPRIX | Distribution |

---

## 🧪 Tests

### Exécution

```bash
# Activer l'environnement
source venv/bin/activate

# Tests d'intégration complets
python -m tests.test_integration

# Sortie attendue:
# ============================================================
#   RESULTS: 7 passed, 0 failed
# ============================================================
```

### Tests Inclus

| # | Test | Description |
|---|------|-------------|
| 1 | Recommendation Engine | Génération de recommandations |
| 2 | User Profiles | Comportement par profil |
| 3 | Portfolio Operations | Achat/vente/métriques |
| 4 | Error Handling | Fonds insuffisants, vente impossible |
| 5 | Explainability | Génération d'explications FR |
| 6 | Batch Analysis | Analyse de marché globale |
| 7 | Trading Flow | Trading basé sur recommandations |

---

## 👥 Équipe

<div align="center">

| Membre | Module | Responsabilité |
|--------|--------|----------------|
| **Rania** | 📈 Forecasting | Prévision des prix (Prophet, MA) |
| **Chiraz** | 📰 Sentiment | Analyse des actualités (NLP FR) |
| **Malek** | ⚠️ Anomaly | Détection d'anomalies statistiques |
| **Aziz** | 🧠 Decision | Engine, Portfolio, Dashboard |

</div>

---

## 🔮 Améliorations Futures

### Court Terme
- [ ] Données en temps réel via API BVMT
- [ ] Plus d'articles pour le sentiment
- [ ] Backtesting multi-années

### Moyen Terme
- [ ] Modèles Deep Learning (LSTM, Transformer)
- [ ] NLP avancé (CamemBERT, FlauBERT)
- [ ] Optimisation de portefeuille (Markowitz)

### Long Terme
- [ ] Application mobile (React Native)
- [ ] Notifications push (email, SMS)
- [ ] Intégration courtiers tunisiens
- [ ] Multi-langue (Arabe, Anglais)

---

## ⚠️ Avertissement

> **Ce système est un outil d'aide à la décision et ne constitue pas un conseil en investissement.**
>
> Les recommandations sont basées sur des modèles quantitatifs et ne garantissent pas les performances futures. Consultez toujours un conseiller financier professionnel avant de prendre des décisions d'investissement.

---

## 📄 Licence

Ce projet est sous licence **MIT**. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

<div align="center">

### 🏆 IHEC CODELAB 2.0 Hackathon

**Développé avec ❤️ en Tunisie**

*Février 2026*

---

<sub>🏦 Building the future of Tunisian FinTech, one algorithm at a time.</sub>

</div>
