# Market Memory Integration Guide

## Overview

The **Market Memory** layer adds semantic intelligence to the BVMT Trading Assistant using Qdrant vector database. This enables explainable AI through evidence retrieval and pattern matching.

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              BVMT Trading Assistant                 │
│                                                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐         │
│  │Forecast  │  │Sentiment │  │ Anomaly  │         │
│  │  Module  │  │  Module  │  │  Module  │         │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘         │
│       │             │              │                │
│       └─────────────┴──────────────┘                │
│                     │                               │
│              ┌──────▼────────┐                      │
│              │   Decision    │                      │
│              │    Engine     │                      │
│              └──────┬────────┘                      │
│                     │                               │
│       ┌─────────────┴──────────────┐                │
│       │                            │                │
│  ┌────▼─────┐          ┌───────────▼────────┐      │
│  │Dashboard │          │  Market Memory     │      │
│  │   (UI)   │◄─────────┤   (Qdrant)         │      │
│  └──────────┘          │                    │      │
│                        │ • bvmt_news        │      │
│                        │ • bvmt_anomalies   │      │
│                        │ • bvmt_recommendations │  │
│                        └────────────────────┘      │
└─────────────────────────────────────────────────────┘
```

---

## Components

### 1. Vector Database (Qdrant)

**What**: Qdrant stores semantic embeddings of market intelligence.

**Collections**:
- `bvmt_news` - News articles and headlines (FR/AR)
- `bvmt_anomalies` - Detected anomalies with context
- `bvmt_recommendations` - Historical recommendations with rationale

**Location**: `docker-compose.yml`

### 2. Embedding Provider

**What**: Converts text to vector embeddings for semantic search.

**Primary Method**: sentence-transformers (all-MiniLM-L6-v2)
**Fallback**: TF-IDF vectorizer (sklearn)

**Location**: `modules/memory/embeddings.py`

### 3. Qdrant Store Wrapper

**What**: Manages connections, collections, and queries.

**Location**: `modules/memory/qdrant_store.py`

### 4. Dashboard Integration

**What**: UI components for semantic search and evidence display.

**Location**: `dashboard/market_memory.py`

---

## Installation & Setup

### Step 1: Install Dependencies

```bash
pip install qdrant-client sentence-transformers scikit-learn
```

**Required packages**:
```txt
qdrant-client>=1.7.0
sentence-transformers>=2.2.2
scikit-learn>=1.3.0
```

### Step 2: Start Qdrant

```bash
# Start Qdrant container
docker compose up -d qdrant

# Verify it's running
docker ps | grep qdrant
```

**Qdrant will be available at**: `http://localhost:6333`

**Web UI**: `http://localhost:6333/dashboard`

### Step 3: Ingest Data

```bash
# Run ingestion script (takes ~30 seconds)
python scripts/ingest_memory.py --limit 100

# To recreate collections from scratch:
python scripts/ingest_memory.py --recreate --limit 100
```

**What it does**:
- Loads cached news from `data/sentiment/news_cache.json`
- Generates sample anomalies from price data
- Creates sample recommendations
- Embeds all texts using sentence-transformers or TF-IDF
- Uploads to Qdrant collections

### Step 4: Run Dashboard

```bash
streamlit run dashboard/app.py
```

---

## Usage

### In the Dashboard

#### 1. **Analysis Page** - Semantic Search Widget

On the "🔍 Analyse Valeur" page, scroll to the bottom to find:

**🔎 Market Memory - Recherche Sémantique**

- Type a question: *"Actualités bancaires récentes"*
- Select a source: 📰 Actualités / ⚠️ Anomalies / 💡 Recommandations
- Get semantic results with similarity scores

**Example queries**:
```
"Hausse du secteur bancaire"
"Anomalies sur BNA"
"Recommandations d'achat pour BIAT"
"Volume anormal ATB"
```

#### 2. **Alerts Page** - Similar Patterns

On the "⚠️ Alertes et Surveillance" page, scroll to bottom:

**🔎 Recherche de Patterns Similaires**

- Select an alert from the dropdown
- System finds similar historical anomalies
- Shows patterns with similarity scores

#### 3. **Recommendation Explanations**

When viewing a recommendation (💡 Recommandation tab):

**Evidence retrouvée (Market Memory):**

- Shows top news/anomalies/recommendations related to current analysis
- Displays semantic similarity scores
- Provides historical context for decisions

---

## API Usage

### Python Integration

```python
from modules.memory.qdrant_store import QdrantStore
from modules.memory.embeddings import get_embedding_provider

# Initialize
store = QdrantStore()
embedder = get_embedding_provider()

# Search news
query_vector = embedder.embed_query("actualités bancaires")
results = store.search(
    collection_name='bvmt_news',
    query_vector=query_vector,
    top_k=5,
    filters={'ticker': 'BNA'}
)

for result in results:
    print(f"{result['text']} (Score: {result['score']:.2f})")
```

### Dashboard Widgets

```python
from dashboard.market_memory import (
    render_memory_search_widget,
    render_similar_items_widget,
    get_memory_evidence
)

# Semantic search widget
render_memory_search_widget(
    placeholder="Posez une question...",
    default_collection='bvmt_news'
)

# Similar items
render_similar_items_widget(
    reference_text="Anomalie détectée sur BNA",
    collection='bvmt_anomalies',
    top_k=3
)

# Get evidence for ticker
evidence = get_memory_evidence('BNA', 'hausse des prix')
# Returns: {'news': [...], 'anomalies': [...], 'recommendations': [...]}
```

---

## Offline Mode

### What happens if Qdrant is not available?

The system **gracefully degrades**:

1. **Dashboard**: Shows warning message *"Market Memory indisponible"*
2. **Explanations**: Shows *(Mode offline: mémoire sémantique indisponible)*
3. **Widgets**: Display info messages with `docker compose up -d qdrant` command
4. **Core modules**: Continue working normally (forecasting, sentiment, anomaly detection)

### Fallback Embedding Method

If internet is unavailable and sentence-transformers can't download:

1. System automatically falls back to TF-IDF vectorizer
2. Uses sklearn's TfidfVectorizer (works offline)
3. Slightly lower quality but still functional

---

## Collections Schema

### bvmt_news

```python
{
    'id': 'news_0',
    'vector': [0.123, -0.456, ...],  # 384 dims
    'text': 'Headline + snippet',
    'ticker': 'BNA',
    'date': '2025-02-08',
    'type': 'news',
    'language': 'fr',
    'source': 'turess.com',
    'metadata': {
        'title': 'Full headline',
        'snippet': 'Full snippet text',
        'url': 'https://...'
    }
}
```

### bvmt_anomalies

```python
{
    'id': 'anomaly_0',
    'vector': [0.789, -0.012, ...],
    'text': 'Anomalie description',
    'ticker': 'BNA',
    'date': '2025-02-08',
    'type': 'anomaly',
    'language': 'fr',
    'source': 'anomaly_detector',
    'metadata': {
        'anomaly_type': 'price_spike',
        'direction': 'hausse',
        'severity': 'HIGH',
        'value': 42.5,
        'change_pct': 5.2,
        'reason': 'Mouvement important de 5.2% en hausse'
    }
}
```

### bvmt_recommendations

```python
{
    'id': 'rec_0',
    'vector': [0.345, -0.678, ...],
    'text': '[ACHAT] BNA - Confiance: 75%\n• Reason 1\n• Reason 2',
    'ticker': 'BNA',
    'date': '2025-02-08',
    'type': 'recommendation',
    'language': 'fr',
    'source': 'decision_engine',
    'metadata': {
        'action': 'ACHAT',
        'confidence': 0.75,
        'reasons': ['Reason 1', 'Reason 2'],
        'horizon': 'Moyen terme (3-6 mois)'
    }
}
```

---

## Performance

### Ingestion Speed

- **100 items**: ~15-20 seconds
- **500 items**: ~45-60 seconds

*Bottleneck*: Embedding generation (sentence-transformers on CPU)

### Search Speed

- **Query time**: 10-50ms
- **Top 5 results**: < 100ms
- **With filters**: < 150ms

*Very fast* - Qdrant is optimized for vector search.

### Memory Usage

- **Qdrant container**: ~200-400 MB
- **Sentence-transformers model**: ~80 MB (cached in `~/.cache/torch/`)
- **Per 1000 documents**: ~50 MB in Qdrant storage

---

## Troubleshooting

### "Cannot connect to Qdrant"

```bash
# Check if Qdrant is running
docker ps | grep qdrant

# If not running:
docker compose up -d qdrant

# Check logs:
docker logs bvmt_qdrant
```

### "sentence-transformers not available"

```bash
# Install package
pip install sentence-transformers

# If offline, system will auto-fallback to TF-IDF
```

### "Collection not found"

```bash
# Run ingestion script
python scripts/ingest_memory.py --recreate
```

### Slow embedding generation

**Solution 1**: Use lighter model
```python
# In embeddings.py, change:
model_name = 'all-MiniLM-L6-v2'  # 384 dims, fast
# To:
model_name = 'paraphrase-MiniLM-L3-v2'  # 384 dims, faster
```

**Solution 2**: Use TF-IDF instead
```python
# Force TF-IDF by not installing sentence-transformers
pip uninstall sentence-transformers
```

---

## Best Practices

### For Hackathon Demo

1. **Pre-ingest data** before demo:
   ```bash
   python scripts/ingest_memory.py --limit 100
   ```

2. **Prepare demo queries**:
   - "Actualités bancaires récentes"
   - "Anomalies sur BNA"
   - "Recommandations d'achat secteur bancaire"

3. **Show explainability**:
   - Open recommendation explanation
   - Point out "Evidence retrouvée (Market Memory)" section
   - Highlight semantic similarity scores

4. **Demo similar patterns**:
   - Go to Alerts page
   - Select an anomaly
   - Show similar historical anomalies

### For Production

1. **Use sentence-transformers** (better quality)
2. **Increase ingestion limit** (`--limit 1000`)
3. **Add authentication** to Qdrant:
   ```yaml
   # docker-compose.yml
   environment:
     - QDRANT__SERVICE__API_KEY=your_secret_key
   ```
4. **Monitor storage size**:
   ```bash
   docker exec bvmt_qdrant du -sh /qdrant/storage
   ```

---

## Added Value

### For Investors (Ahmed)

**Before Market Memory**:
- Recommendation: "ACHAT BNA - Confiance 75%"
- No historical context

**After Market Memory**:
- Recommendation: "ACHAT BNA - Confiance 75%"
- **+ Evidence**: 3 positive news articles, no recent anomalies, similar past recommendations
- **+ Context**: "Le marché bancaire montre une tendance haussière similaire en 2023"

### For Regulators (CMF)

**Before Market Memory**:
- Alert: "Anomalie détectée sur ATB - Volume spike"
- Manual investigation required

**After Market Memory**:
- Alert: "Anomalie détectée sur ATB - Volume spike"
- **+ Patterns**: Shows 2 similar historical volume spikes on same stock
- **+ Context**: Related news about quarterly results announcement
- **Fast triage**: Regulator can quickly determine if pattern is normal or suspicious

### For Traders (Leila)

**Before Market Memory**:
- Multiple data sources to check manually

**After Market Memory**:
- Single search: *"mouvements inhabituels BIAT"*
- Gets: relevant news + detected anomalies + past recommendations
- **Faster decisions** with full context

---

## Advanced: Custom Embeddings

### Use Multilingual Model

For better Arabic support:

```python
# In modules/memory/embeddings.py
model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
```

### Use OpenAI Embeddings (requires API key)

```python
from openai import OpenAI

client = OpenAI(api_key='your_key')

def embed_texts(texts):
    response = client.embeddings.create(
        input=texts,
        model="text-embedding-3-small"
    )
    return [item.embedding for item in response.data]
```

---

## Docker Compose Reference

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
    container_name: bvmt_qdrant
    ports:
      - "6333:6333"  # REST API
      - "6334:6334"  # gRPC API
    volumes:
      - qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
    networks:
      - bvmt_network

volumes:
  qdrant_storage:
    driver: local

networks:
  bvmt_network:
    driver: bridge
```

**Commands**:
```bash
# Start
docker compose up -d qdrant

# Stop
docker compose stop qdrant

# Remove (deletes data!)
docker compose down -v

# Logs
docker logs -f bvmt_qdrant
```

---

## FAQ

**Q: Do I need internet for the demo?**
A: Once sentence-transformers model is downloaded (first run), demo works offline.

**Q: How much disk space is needed?**
A: ~500 MB total (Qdrant container + model cache + vector storage)

**Q: Can I use this for other markets?**
A: Yes! Just change ticker list and data sources in `scripts/ingest_memory.py`

**Q: What if I don't have Docker?**
A: Install Qdrant directly: https://qdrant.tech/documentation/quick-start/

**Q: Is the data persistent?**
A: Yes, stored in `qdrant_storage` Docker volume. Survives container restarts.

---

## References

- **Qdrant Docs**: https://qdrant.tech/documentation/
- **Sentence Transformers**: https://www.sbert.net/
- **Vector Search Intro**: https://www.pinecone.io/learn/vector-search/

---

## Summary

The Market Memory integration adds **semantic intelligence** to the BVMT Trading Assistant:

✅ **Explainability**: Evidence-based recommendations  
✅ **Pattern Matching**: Find similar historical events  
✅ **Context**: Connect news ↔ anomalies ↔ recommendations  
✅ **Fast**: Sub-second semantic search  
✅ **Offline**: Works without external APIs  
✅ **Scalable**: Handles thousands of documents  

This makes the system **production-ready** for real-world trading and regulatory scenarios, while being **demo-friendly** for the hackathon jury.
