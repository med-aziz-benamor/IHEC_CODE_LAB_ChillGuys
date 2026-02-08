"""
Sentiment Analysis Module
=========================
Analyzes sentiment of financial news articles (French language).
Uses pre-cached news data and keyword-based sentiment classification.
Integrated with Module2 advanced sentiment analyzer.
"""

import json
import os
import csv
import ast
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.shared.data_loader import get_stock_name
from modules.shared.data_loader import STOCK_NAMES

# ============================================================================
# ADVANCED KEYWORD-BASED SENTIMENT CORRECTION (from Module2)
# ============================================================================

_STRONG_NEGATIVE = [
    "dans le rouge",
    "chute",
    "effondrement",
    "krach",
    "pertes",
    "deficit",
    "faillite",
    "recession",
    "crise",
    "licenciements",
    "scandale",
    "fraude",
]

_MODERATE_NEGATIVE = [
    "baisse",
    "recul",
    "repli",
    "ralentissement",
    "incertitude",
    "difficultes",
    "difficulte",
    "avertissement sur resultats",
    "avertissement",
]

_STRONG_POSITIVE = [
    "dans le vert",
    "bond",
    "envolee",
    "benefice record",
    "acquisition",
    "fusion",
]

_MODERATE_POSITIVE = [
    "hausse",
    "progression",
    "croissance",
    "amelioration",
    "rebond",
    "optimisme",
    "gain",
]


def _normalize_text(text: str) -> str:
    """Normalize text for keyword matching"""
    return " ".join(text.lower().split()) if text else ""


def analyze_financial_keywords(text: str) -> Dict[str, Any]:
    """
    Analyze financial keywords in text to suggest sentiment.
    
    Args:
        text: Text to analyze
    
    Returns:
        Dictionary with suggested_label, neg_score, pos_score, matched_keywords
    """
    normalized = _normalize_text(text)

    matched = {
        "strong_negative": [],
        "moderate_negative": [],
        "strong_positive": [],
        "moderate_positive": [],
    }

    neg_score = 0.0
    pos_score = 0.0

    for kw in _STRONG_NEGATIVE:
        if kw in normalized:
            matched["strong_negative"].append(kw)
            neg_score += 2.0

    for kw in _MODERATE_NEGATIVE:
        if kw in normalized:
            matched["moderate_negative"].append(kw)
            neg_score += 1.0

    for kw in _STRONG_POSITIVE:
        if kw in normalized:
            matched["strong_positive"].append(kw)
            pos_score += 2.0

    for kw in _MODERATE_POSITIVE:
        if kw in normalized:
            matched["moderate_positive"].append(kw)
            pos_score += 1.0

    suggested = "NEU"
    if pos_score - neg_score >= 1.0:
        suggested = "POS"
    elif neg_score - pos_score >= 1.0:
        suggested = "NEG"

    return {
        "suggested_label": suggested,
        "neg_score": neg_score,
        "pos_score": pos_score,
        "matched_keywords": matched,
    }


def correct_sentiment_with_keywords(model_result: Dict[str, Any], text: str) -> Dict[str, Any]:
    """
    Correct ML sentiment predictions using financial keywords.
    Overrides weak ML predictions when strong keywords are detected.
    
    Args:
        model_result: Dictionary with label, score, confidence from ML model
        text: Original text to analyze
    
    Returns:
        Corrected sentiment dictionary
    """
    result = dict(model_result or {})
    result.setdefault("label", "NEU")
    result.setdefault("score", 0.0)
    result.setdefault("confidence", 0.0)
    result["correction_applied"] = False

    keyword_analysis = analyze_financial_keywords(text)
    suggested = keyword_analysis.get("suggested_label", "NEU")

    # Apply correction if keywords suggest different sentiment
    if suggested in ("POS", "NEG") and suggested != result["label"]:
        result["original_label"] = result["label"]
        result["label"] = suggested
        result["correction_applied"] = True
        result["score"] = 0.7 if suggested == "POS" else -0.7
        result["confidence"] = max(float(result.get("confidence") or 0.0), 0.7)
        result["keyword_analysis"] = keyword_analysis

    return result

# Module2 paths (optional integration)
_MODULE2_DIR = Path(__file__).parent / "Module2"
_MODULE2_CSVS = [
    _MODULE2_DIR / "sentiment_results.csv",
    _MODULE2_DIR / "resultats.csv",
]
_MODULE2_DB = _MODULE2_DIR / "bvmt_sentiment.db"

_MODULE2_CACHE = None


def _build_ticker_map() -> Dict[str, str]:
    """Map Module2 tickers to ISIN stock codes."""
    reverse = {}
    for code, name in STOCK_NAMES.items():
        reverse[name] = code
    return reverse


def _parse_tickers(value: str) -> List[str]:
    if not value:
        return []
    try:
        return json.loads(value)
    except Exception:
        try:
            return ast.literal_eval(value)
        except Exception:
            return []


def _load_module2_csv_rows() -> List[Dict]:
    """Load Module2 sentiment CSV rows if available."""
    global _MODULE2_CACHE
    if _MODULE2_CACHE is not None:
        return _MODULE2_CACHE

    rows = []
    for path in _MODULE2_CSVS:
        if not path.exists():
            continue
        try:
            with path.open('r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append(row)
        except Exception:
            continue

    _MODULE2_CACHE = rows
    return rows


def _get_module2_sentiment(stock_code: str, date: str = None) -> Dict:
    """Try to compute sentiment from Module2 CSV outputs."""
    rows = _load_module2_csv_rows()
    if not rows:
        return {}

    ticker_map = _build_ticker_map()
    stock_name = get_stock_name(stock_code)

    matches = []
    for row in rows:
        tickers = _parse_tickers(row.get('tickers', ''))
        mapped_codes = []
        for t in tickers:
            if t in STOCK_NAMES:
                mapped_codes.append(t)
            elif t in ticker_map:
                mapped_codes.append(ticker_map[t])
        if stock_code in mapped_codes or stock_name in tickers:
            matches.append(row)

    if not matches:
        return {}

    def _to_float(val):
        try:
            return float(val)
        except Exception:
            return None

    sentiments = []
    confidences = []
    headlines = []

    for row in matches:
        score = _to_float(row.get('corrected_score')) or _to_float(row.get('original_score')) or 0.0
        conf = _to_float(row.get('corrected_confidence')) or _to_float(row.get('original_confidence')) or 0.0
        sentiments.append(score)
        confidences.append(conf)
        headlines.append({
            'headline': row.get('title', ''),
            'source': row.get('source', 'Unknown'),
            'date': row.get('published_at', ''),
            'sentiment': score,
        })

    avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0.0
    avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
    headlines.sort(key=lambda x: x['date'], reverse=True)

    return {
        'stock_code': stock_code,
        'stock_name': stock_name,
        'date': date or datetime.now().strftime('%Y-%m-%d'),
        'sentiment_score': float(avg_sentiment),
        'confidence': float(avg_confidence),
        'num_articles': len(matches),
        'sample_headlines': headlines[:5],
        'summary': f"Sentiment Module2: {avg_sentiment:+.2f} (n={len(matches)})"
    }


# ============================================================================
# ADVANCED SENTIMENT ANALYZERS (from Module2)
# ============================================================================

class HuggingFaceSentimentAnalyzer:
    """
    Sentiment analyzer using HuggingFace transformers with keyword correction.
    """
    def __init__(self, model_name: str = None, device: int = -1):
        self.model_name = model_name or os.getenv(
            "SENTIMENT_MODEL", "cardiffnlp/twitter-xlm-roberta-base-sentiment"
        )
        self.device = device
        self._pipeline = None

    def _ensure_pipeline(self) -> None:
        """Lazy load the HuggingFace pipeline"""
        if self._pipeline is not None:
            return
        try:
            from transformers import pipeline
        except Exception as exc:
            raise ImportError("transformers not available. Install: pip install transformers torch") from exc
        self._pipeline = pipeline(
            "sentiment-analysis",
            model=self.model_name,
            device=self.device,
        )

    def _map_label(self, raw_label: str) -> str:
        """Map various label formats to POS/NEG/NEU"""
        label = (raw_label or "").lower().strip()
        if "neg" in label or label in {"label_0", "0", "1 star", "2 stars"}:
            return "NEG"
        if "pos" in label or label in {"label_2", "5 stars", "4 stars"}:
            return "POS"
        if "neutral" in label or label in {"label_1", "3 stars"}:
            return "NEU"
        return "NEU"

    def analyze(self, text: str, apply_keyword_correction: bool = True) -> Dict[str, Any]:
        """
        Analyze sentiment using HuggingFace model with optional keyword correction.
        
        Args:
            text: Text to analyze
            apply_keyword_correction: Whether to apply keyword-based correction
        
        Returns:
            Dictionary with label, score, confidence
        """
        if not text:
            return {"label": "NEU", "score": 0.0, "confidence": 0.0}

        self._ensure_pipeline()
        outputs = self._pipeline(text[:512])  # Limit to 512 chars
        output = outputs[0] if isinstance(outputs, list) else outputs

        label = self._map_label(output.get("label"))
        score = float(output.get("score", 0.0))

        # Convert to signed score (-1 to +1)
        if label == "POS":
            signed_score = score
        elif label == "NEG":
            signed_score = -score
        else:
            signed_score = 0.0

        result = {
            "label": label,
            "score": signed_score,
            "confidence": score if label != "NEU" else 0.5,
        }

        if apply_keyword_correction:
            return correct_sentiment_with_keywords(result, text)

        return result


class GroqSentimentAnalyzer:
    """
    Sentiment analyzer using Groq API (LLM-based) with keyword correction.
    """
    def __init__(self, model_name: str = None):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in environment")
        self.model_name = model_name or os.getenv("GROQ_MODEL", "llama3-8b-8192")

        try:
            from groq import Groq
        except Exception as exc:
            raise ImportError("groq package not available. Install: pip install groq") from exc

        self._client = Groq(api_key=api_key)

    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        content = content.strip()
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                return data
        except Exception:
            pass

        # Try to extract JSON from text
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                if isinstance(data, dict):
                    return data
            except Exception:
                pass

        return {}

    def analyze(self, text: str, apply_keyword_correction: bool = True) -> Dict[str, Any]:
        """
        Analyze sentiment using Groq LLM with optional keyword correction.
        
        Args:
            text: Text to analyze
            apply_keyword_correction: Whether to apply keyword-based correction
        
        Returns:
            Dictionary with label, score, confidence
        """
        if not text:
            return {"label": "NEU", "score": 0.0, "confidence": 0.0}

        system = (
            "You are a sentiment classifier for financial news titles. "
            "Return JSON with keys: label (POS/NEG/NEU), "
            "score (-1.0 to 1.0), confidence (0.0 to 1.0)."
        )
        user = f"Title: {text}\nReturn JSON only."

        response = self._client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )

        content = response.choices[0].message.content or ""
        data = self._parse_response(content)

        label = (data.get("label") or "NEU").upper().strip()
        if label not in {"POS", "NEG", "NEU"}:
            label = "NEU"

        score = float(data.get("score", 0.0))
        confidence = float(data.get("confidence", 0.0))

        result = {"label": label, "score": score, "confidence": confidence}
        if apply_keyword_correction:
            return correct_sentiment_with_keywords(result, text)
        return result


class EnhancedSentimentAnalyzer:
    """
    Unified sentiment analyzer that selects best available method.
    Priority: Groq API > HuggingFace > Simple Keywords
    """
    def __init__(self, provider: str = "auto"):
        """
        Args:
            provider: 'auto', 'groq', 'huggingface', or 'keywords'
        """
        self.provider = provider.lower().strip()
        self._impl = None

    def _get_impl(self):
        """Lazy load the best available implementation"""
        if self._impl is not None:
            return self._impl

        if self.provider == "groq":
            try:
                self._impl = GroqSentimentAnalyzer()
                return self._impl
            except Exception:
                pass

        if self.provider in {"huggingface", "hf"}:
            try:
                self._impl = HuggingFaceSentimentAnalyzer()
                return self._impl
            except Exception:
                pass

        if self.provider == "auto":
            # Try Groq first (fastest)
            if os.getenv("GROQ_API_KEY"):
                try:
                    self._impl = GroqSentimentAnalyzer()
                    return self._impl
                except Exception:
                    pass

            # Try HuggingFace
            try:
                self._impl = HuggingFaceSentimentAnalyzer()
                return self._impl
            except Exception:
                pass

        # Fallback to simple keywords
        return None

    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using best available method.
        
        Args:
            text: Text to analyze
        
        Returns:
            Dictionary with sentiment_score, confidence, label
        """
        impl = self._get_impl()
        
        if impl is None:
            # Use simple keyword fallback
            from . import analyzer as old_analyzer
            if hasattr(old_analyzer, 'simple_keyword_sentiment'):
                result = old_analyzer.simple_keyword_sentiment(text)
            else:
                # Ultra-simple fallback
                result = analyze_financial_keywords(text)
                result = {
                    'sentiment_score': 0.7 if result['suggested_label'] == 'POS' else (-0.7 if result['suggested_label'] == 'NEG' else 0.0),
                    'confidence': 0.6,
                    'label': result['suggested_label'],
                }
            return {
                'sentiment_score': result.get('sentiment_score', 0.0),
                'confidence': result.get('confidence', 0.5),
                'label': result.get('label', 'NEU'),
                'method': 'keywords',
            }
        
        # Use advanced analyzer
        try:
            result = impl.analyze(text)
            return {
                'sentiment_score': result['score'],
                'confidence': result['confidence'],
                'label': result['label'],
                'method': 'groq' if isinstance(impl, GroqSentimentAnalyzer) else 'huggingface',
                'correction_applied': result.get('correction_applied', False),
            }
        except Exception as e:
            # Fallback on error
            result = analyze_financial_keywords(text)
            return {
                'sentiment_score': 0.7 if result['suggested_label'] == 'POS' else (-0.7 if result['suggested_label'] == 'NEG' else 0.0),
                'confidence': 0.5,
                'label': result['suggested_label'],
                'method': 'keywords_fallback',
                'error': str(e),
            }


# ============================================================================
# SIMPLE KEYWORD ANALYSIS (Legacy - kept for backward compatibility)
# ============================================================================

POSITIVE_KEYWORDS_FR = [
    'croissance', 'hausse', 'profit', 'bénéfice', 'succès', 'réussi',
    'nouveau contrat', 'partenariat', 'innovation', 'expansion',
    'solide', 'record', 'amélioration', 'robuste', 'positif', 'fort',
    'excellent', 'performance', 'leadership', 'investit', 'lancé',
    'modernise', 'soutien', 'perspectives positives', 'résultats exceptionnels',
    'croissance', 'développement', 'opportunité', 'succès'
]

NEGATIVE_KEYWORDS_FR = [
    'perte', 'baisse', 'crise', 'difficultés', 'licenciement', 'problème',
    'dette', 'risque', 'chute', 'scandale', 'défis', 'confrontée',
    'inquiétudes', 'pression', 'prudence', 'restructuration',
    'négatif', 'échec', 'recul', 'menace', 'tension', 'faible'
]

NEUTRAL_KEYWORDS_FR = [
    'maintient', 'stabilité', 'prudente', 'modérée', 'observée',
    'contexte', 'stratégie', 'annonce', 'prévue', 'attendue'
]


def load_news_cache() -> Dict:
    """
    Load pre-cached news data from JSON file.
    
    Returns:
        Dictionary with cached news data
    """
    # Try multiple possible locations
    possible_paths = [
        'data/sentiment/news_cache.json',
        '../data/sentiment/news_cache.json',
        '../../data/sentiment/news_cache.json',
        os.path.join(os.path.dirname(__file__), '../../data/sentiment/news_cache.json'),
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading cache from {path}: {e}")
                continue
    
    # Return empty cache if file not found
    print("Warning: News cache file not found. Using empty cache.")
    return {}


# Global cache
_NEWS_CACHE = None


def get_news_cache() -> Dict:
    """Get news cache (loads once and caches in memory)"""
    global _NEWS_CACHE
    
    if _NEWS_CACHE is None:
        _NEWS_CACHE = load_news_cache()
    
    return _NEWS_CACHE


def classify_sentiment_keywords(text: str) -> float:
    """
    Classify sentiment using keyword matching.
    
    Args:
        text: Text to analyze (French)
    
    Returns:
        Sentiment score from -1 (very negative) to +1 (very positive)
    """
    text_lower = text.lower()
    
    # Count positive and negative keywords
    pos_count = sum(1 for word in POSITIVE_KEYWORDS_FR if word in text_lower)
    neg_count = sum(1 for word in NEGATIVE_KEYWORDS_FR if word in text_lower)
    neutral_count = sum(1 for word in NEUTRAL_KEYWORDS_FR if word in text_lower)
    
    total_count = pos_count + neg_count + neutral_count
    
    if total_count == 0:
        return 0.0  # Neutral if no keywords found
    
    # Calculate weighted score
    # Positive contributes +1, negative -1, neutral 0
    score = (pos_count - neg_count) / total_count
    
    # Ensure score is between -1 and 1
    return max(-1.0, min(1.0, score))


def analyze_headline(headline: str) -> Dict:
    """
    Analyze sentiment of a single headline.
    
    Args:
        headline: News headline text
    
    Returns:
        Dictionary with sentiment analysis
    """
    score = classify_sentiment_keywords(headline)
    
    # Classify as positive, negative, or neutral
    if score > 0.2:
        classification = 'positive'
    elif score < -0.2:
        classification = 'negative'
    else:
        classification = 'neutral'
    
    return {
        'headline': headline,
        'sentiment': score,
        'classification': classification
    }


def get_sentiment_score(stock_code: str, date: str = None, use_advanced: bool = False, provider: str = "auto") -> dict:
    """
    Get sentiment analysis for a stock based on recent news.
    
    Args:
        stock_code: ISIN code
        date: Optional date (format: 'YYYY-MM-DD'). If None, uses current date.
        use_advanced: If True, use ML-based sentiment analysis (HuggingFace/Groq)
        provider: 'auto', 'groq', 'huggingface', or 'keywords'
    
    Returns:
        {
            'stock_code': str,
            'stock_name': str,
            'date': str,
            'sentiment_score': float,  # -1 to +1
            'confidence': float,       # 0 to 1
            'num_articles': int,
            'sample_headlines': [
                {'headline': str, 'source': str, 'sentiment': float, 'date': str},
                ...
            ],
            'summary': str,
            'method': str  # 'module2_csv', 'groq', 'huggingface', or 'keywords'
        }
    """
    try:
        stock_name = get_stock_name(stock_code)
        
        # Try Module2 sentiment first (if available)
        module2_result = _get_module2_sentiment(stock_code, date)
        if module2_result:
            module2_result['method'] = 'module2_csv'
            return module2_result
        
        # If advanced ML requested
        if use_advanced:
            try:
                analyzer = EnhancedSentimentAnalyzer(provider=provider)
                # Analyze using stock name as context
                text = f"{stock_name} - Analyse de tendance de marché"
                result = analyzer.analyze(text)
                
                return {
                    'stock_code': stock_code,
                    'stock_name': stock_name,
                    'date': date or datetime.now().strftime('%Y-%m-%d'),
                    'sentiment_score': result['sentiment_score'],
                    'confidence': result['confidence'],
                    'num_articles': 1,
                    'sample_headlines': [],
                    'summary': f"ML Analysis ({result.get('method')}): {result['sentiment_score']:+.2f}",
                    'method': result.get('method', 'unknown'),
                    'correction_applied': result.get('correction_applied', False)
                }
            except Exception as e:
                # Fall through to cache/keyword analysis
                print(f"Advanced analysis failed, using fallback: {e}")

        # Load news cache
        cache = get_news_cache()
        
        # Get articles for this stock
        if stock_code not in cache:
            # No cached data for this stock
            return {
                'stock_code': stock_code,
                'stock_name': get_stock_name(stock_code),
                'date': date or datetime.now().strftime('%Y-%m-%d'),
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'num_articles': 0,
                'sample_headlines': [],
                'summary': 'Aucune actualité disponible pour cette valeur.'
            }
        
        stock_data = cache[stock_code]
        articles = stock_data.get('articles', [])
        
        if not articles:
            return {
                'stock_code': stock_code,
                'stock_name': stock_data.get('stock_name', get_stock_name(stock_code)),
                'date': date or datetime.now().strftime('%Y-%m-%d'),
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'num_articles': 0,
                'sample_headlines': [],
                'summary': 'Aucune actualité disponible pour cette valeur.'
            }
        
        # Analyze all articles
        sentiments = []
        analyzed_headlines = []
        
        for article in articles:
            headline = article.get('headline', '')
            if not headline:
                continue
            
            analysis = analyze_headline(headline)
            sentiments.append(analysis['sentiment'])
            
            analyzed_headlines.append({
                'headline': headline,
                'source': article.get('source', 'Unknown'),
                'date': article.get('date', ''),
                'sentiment': analysis['sentiment']
            })
        
        # Calculate aggregate sentiment
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
            
            # Confidence based on number of articles and agreement
            num_articles = len(sentiments)
            
            # Higher confidence with more articles
            volume_confidence = min(num_articles / 10, 0.8)
            
            # Higher confidence if sentiments agree
            sentiment_std = (sum((s - avg_sentiment) ** 2 for s in sentiments) / len(sentiments)) ** 0.5
            agreement_confidence = max(0.5, 1.0 - sentiment_std)
            
            # Combined confidence
            confidence = (volume_confidence + agreement_confidence) / 2
        else:
            avg_sentiment = 0.0
            confidence = 0.0
        
        # Generate summary
        if avg_sentiment > 0.3:
            summary = f"Sentiment global très positif ({avg_sentiment:.2f}). Les actualités montrent des perspectives favorables."
        elif avg_sentiment > 0.1:
            summary = f"Sentiment légèrement positif ({avg_sentiment:.2f}). Les nouvelles sont plutôt encourageantes."
        elif avg_sentiment < -0.3:
            summary = f"Sentiment négatif ({avg_sentiment:.2f}). Les actualités révèlent des préoccupations."
        elif avg_sentiment < -0.1:
            summary = f"Sentiment légèrement négatif ({avg_sentiment:.2f}). Certaines inquiétudes sont présentes."
        else:
            summary = f"Sentiment neutre ({avg_sentiment:.2f}). Les actualités sont équilibrées."
        
        # Sort headlines by date (most recent first)
        analyzed_headlines.sort(key=lambda x: x['date'], reverse=True)
        
        return {
            'stock_code': stock_code,
            'stock_name': stock_data.get('stock_name', get_stock_name(stock_code)),
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'sentiment_score': float(avg_sentiment),
            'confidence': float(confidence),
            'num_articles': len(articles),
            'sample_headlines': analyzed_headlines[:5],  # Top 5 most recent
            'summary': summary
        }
    
    except Exception as e:
        # Return neutral sentiment on error
        return {
            'stock_code': stock_code,
            'stock_name': get_stock_name(stock_code),
            'date': date or datetime.now().strftime('%Y-%m-%d'),
            'sentiment_score': 0.0,
            'confidence': 0.0,
            'num_articles': 0,
            'sample_headlines': [],
            'summary': f'Erreur lors de l\'analyse de sentiment: {str(e)}',
            'error': str(e)
        }


def get_market_sentiment() -> Dict:
    """
    Get overall market sentiment across all cached stocks.
    
    Returns:
        Dictionary with aggregate market sentiment
    """
    # Try Module2 sentiment if available
    rows = _load_module2_csv_rows()
    if rows:
        ticker_map = _build_ticker_map()
        by_code = {}
        for row in rows:
            tickers = _parse_tickers(row.get('tickers', ''))
            mapped_codes = []
            for t in tickers:
                if t in STOCK_NAMES:
                    mapped_codes.append(t)
                elif t in ticker_map:
                    mapped_codes.append(ticker_map[t])
            if not mapped_codes:
                continue
            try:
                score = float(row.get('corrected_score') or row.get('original_score') or 0.0)
            except Exception:
                score = 0.0
            for code in mapped_codes:
                by_code.setdefault(code, []).append(score)

        sentiments = []
        positive = negative = neutral = 0
        for code, scores in by_code.items():
            avg = sum(scores) / len(scores)
            sentiments.append(avg)
            if avg > 0.2:
                positive += 1
            elif avg < -0.2:
                negative += 1
            else:
                neutral += 1

        overall = sum(sentiments) / len(sentiments) if sentiments else 0.0
        return {
            'overall_sentiment': float(overall),
            'num_stocks': len(by_code),
            'positive_stocks': positive,
            'negative_stocks': negative,
            'neutral_stocks': neutral
        }

    cache = get_news_cache()
    
    if not cache:
        return {
            'overall_sentiment': 0.0,
            'num_stocks': 0,
            'positive_stocks': 0,
            'negative_stocks': 0,
            'neutral_stocks': 0
        }
    
    sentiments = []
    positive = 0
    negative = 0
    neutral = 0
    
    for stock_code in cache.keys():
        result = get_sentiment_score(stock_code)
        score = result['sentiment_score']
        sentiments.append(score)
        
        if score > 0.2:
            positive += 1
        elif score < -0.2:
            negative += 1
        else:
            neutral += 1
    
    overall = sum(sentiments) / len(sentiments) if sentiments else 0.0
    
    return {
        'overall_sentiment': float(overall),
        'num_stocks': len(cache),
        'positive_stocks': positive,
        'negative_stocks': negative,
        'neutral_stocks': neutral
    }


# Testing
if __name__ == "__main__":
    print("Testing sentiment analysis module...")
    
    # Test cache loading
    cache = get_news_cache()
    print(f"✓ Loaded news cache with {len(cache)} stocks\n")
    
    # Test sentiment analysis for cached stocks
    test_stocks = list(cache.keys())[:5]  # Test first 5
    
    for stock_code in test_stocks:
        print(f"{'='*70}")
        result = get_sentiment_score(stock_code)
        
        print(f"Stock: {result['stock_name']} ({result['stock_code']})")
        print(f"Sentiment Score: {result['sentiment_score']:.2f} (-1 to +1)")
        print(f"Confidence: {result['confidence']:.0%}")
        print(f"Articles Analyzed: {result['num_articles']}")
        print(f"Summary: {result['summary']}")
        
        if result['sample_headlines']:
            print(f"\nRecent Headlines:")
            for i, headline in enumerate(result['sample_headlines'][:3], 1):
                sentiment_emoji = '😊' if headline['sentiment'] > 0.2 else '😟' if headline['sentiment'] < -0.2 else '😐'
                print(f"  {i}. [{headline['date']}] {headline['headline']}")
                print(f"     Source: {headline['source']} | Sentiment: {sentiment_emoji} {headline['sentiment']:.2f}")
        
        print()
    
    # Test market sentiment
    print(f"{'='*70}")
    market = get_market_sentiment()
    print("Market Sentiment Overview:")
    print(f"  Overall Sentiment: {market['overall_sentiment']:.2f}")
    print(f"  Stocks Analyzed: {market['num_stocks']}")
    print(f"  Positive: {market['positive_stocks']}")
    print(f"  Negative: {market['negative_stocks']}")
    print(f"  Neutral: {market['neutral_stocks']}")
    
    print("\n✅ Sentiment analysis module test complete!")
