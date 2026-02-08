# Guide d'Integration - IHEC CODELAB 2.0

## Architecture du Projet

```
modules/
├── decision/          <- VOTRE MODULE (Aziz)
│   ├── engine.py      <- Moteur de decision principal
│   ├── portfolio.py   <- Simulation de portefeuille
│   ├── explainer.py   <- Systeme d'explicabilite
│   ├── mocks.py       <- Donnees simulees (a remplacer)
│   └── stock_data.py  <- Chargement des donnees BVMT
│
├── forecasting/       <- MODULE RANIA
│   └── predict.py     <- Votre module ici
│
├── sentiment/         <- MODULE CHIRAZ
│   └── analyzer.py    <- Votre module ici
│
└── anomaly/           <- MODULE MALEK
    └── detector.py    <- Votre module ici
```

---

## POUR RANIA (Forecasting)

### Ce dont le Decision Engine a besoin:

```python
# Dans modules/forecasting/predict.py

def predict_next_days(stock_code: str, n_days: int = 5) -> dict:
    """
    Predit les prix pour les N prochains jours.

    Args:
        stock_code: Code ISIN (ex: 'TN0001600154')
        n_days: Nombre de jours a predire

    Returns:
        {
            'trend': float,          # Tendance globale (-0.1 a 0.1)
            'confidence': float,     # Confiance du modele (0 a 1)
            'predictions': [         # Prix predits
                {'day': 1, 'close': 52.0},
                {'day': 2, 'close': 52.5},
                ...
            ]
        }

    Exemple:
        {'trend': 0.032, 'confidence': 0.85, 'predictions': [...]}
        = +3.2% de hausse attendue avec 85% de confiance
    """
```

### Comment je vais l'appeler:

```python
from modules.forecasting.predict import predict_next_days

result = predict_next_days('TN0001600154', n_days=5)
trend = result['trend']  # Je veux ce chiffre!
```

---

## POUR CHIRAZ (Sentiment)

### Ce dont le Decision Engine a besoin:

```python
# Dans modules/sentiment/analyzer.py

def analyze_sentiment(stock_code: str) -> dict:
    """
    Analyse le sentiment des actualites pour une action.

    Args:
        stock_code: Code ISIN

    Returns:
        {
            'score': float,           # Score sentiment (-1 a 1)
            'num_articles': int,      # Nombre d'articles analyses
            'sample_headlines': list, # Exemples de titres
            'sources': list           # Sources utilisees
        }

    Exemple:
        {'score': 0.65, 'num_articles': 5, ...}
        = Sentiment positif (0.65) base sur 5 articles
    """
```

### Interpretation du score:
- `score > 0.4` = Sentiment positif (signal d'achat)
- `score < -0.4` = Sentiment negatif (signal de vente)
- Entre les deux = Neutre

---

## POUR MALEK (Anomaly Detection)

### Ce dont le Decision Engine a besoin:

```python
# Dans modules/anomaly/detector.py

def detect_anomalies(stock_code: str) -> dict:
    """
    Detecte les anomalies de trading.

    Args:
        stock_code: Code ISIN

    Returns:
        {
            'volume_spike': bool,     # Pic de volume anormal
            'price_spike': bool,      # Variation de prix anormale
            'any_anomaly': bool,      # Une anomalie detectee
            'anomaly_score': float,   # Severite (0 a 1)
            'details': str            # Description
        }

    Exemple:
        {'volume_spike': True, 'any_anomaly': True, ...}
        = Attention! Volume anormal detecte
    """
```

### Impact sur le score:
- `volume_spike = True` -> -2 points (suspicion)
- `price_spike = True` -> -1 point
- `any_anomaly = False` -> +1 point (normal = bon signe)

---

## Comment Activer l'Integration

Une fois vos modules prets, editez `modules/decision/engine.py`:

```python
# Ligne 15: Changez cette variable
USE_MOCKS = False  # Au lieu de True

# Et ajoutez vos imports:
from modules.forecasting.predict import predict_next_days
from modules.sentiment.analyzer import analyze_sentiment
from modules.anomaly.detector import detect_anomalies
```

---

## Test Rapide

```bash
# Verifier que tout fonctionne
python -m tests.test_integration

# Lancer la demo
python demo.py

# Lancer l'API (pour le dashboard)
python api.py
```

---

## API REST Disponible

L'API est prete pour le dashboard a `http://localhost:5000`:

| Endpoint | Description |
|----------|-------------|
| GET /api/stocks | Liste toutes les actions |
| GET /api/recommend/TN0001600154 | Recommendation pour une action |
| GET /api/market/summary | Resume du marche |
| GET /api/portfolio | Etat du portefeuille |
| POST /api/portfolio/buy | Executer un achat |

---

## Questions?

Le Decision Engine est pret. Vos modules seront integres des qu'ils sont termines!
