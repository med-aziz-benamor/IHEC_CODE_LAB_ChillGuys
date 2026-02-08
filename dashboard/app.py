#!/usr/bin/env python3
"""
BVMT Trading Assistant - Dashboard
===================================
IHEC CODELAB 2.0 Hackathon

A professional, production-grade Streamlit dashboard for intelligent
stock analysis and portfolio management on the Tunisian stock market.

Usage:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
from pathlib import Path

# Add parent directory to path for module imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# ============================================================================
# INTERNATIONALIZATION
# ============================================================================
try:
    from dashboard.i18n import t, set_language, get_current_language, is_rtl, get_rtl_css, render_language_selector, get_profile_name
except ImportError:
    # Fallback if i18n not available
    def t(key, **kwargs): return key
    def set_language(lang): pass
    def get_current_language(): return 'fr'
    def is_rtl(): return False
    def get_rtl_css(): return ""
    def render_language_selector(key): return 'fr'
    def get_profile_name(profile): return profile

# ============================================================================
# UI CONFIGURATION (Colors, Typography, Spacing)
# ============================================================================
try:
    from dashboard.ui_config import COLORS, get_component_styles
except ImportError:
    # Fallback colors
    COLORS = {
        'primary': '#1E40AF',
        'success': '#059669',
        'danger': '#DC2626',
        'warning': '#D97706',
    }
    def get_component_styles(): return ""

# ============================================================================
# ONBOARDING SYSTEM
# ============================================================================
try:
    from dashboard.onboarding import (
        run_onboarding, should_show_onboarding, get_user_profile,
        reset_onboarding, PROFILES
    )
    ONBOARDING_AVAILABLE = True
except ImportError:
    ONBOARDING_AVAILABLE = False
    def run_onboarding(): pass
    def should_show_onboarding(): return False
    def get_user_profile(): return None
    def reset_onboarding(): pass
    PROFILES = {}

# ============================================================================
# MARKET MEMORY SYSTEM
# ============================================================================
try:
    from dashboard.market_memory import (
        render_memory_search_widget, render_similar_items_widget,
        render_memory_status_badge, get_memory_evidence
    )
    MARKET_MEMORY_AVAILABLE = True
except ImportError:
    MARKET_MEMORY_AVAILABLE = False
    def render_memory_search_widget(*args, **kwargs): pass
    def render_similar_items_widget(*args, **kwargs): pass
    def render_memory_status_badge(): pass
    def get_memory_evidence(*args, **kwargs): return {}

# ============================================================================
# PAGE CONFIG - Must be first Streamlit command
# ============================================================================
st.set_page_config(
    page_title="BVMT Trading Assistant",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CONSTANTS
# ============================================================================
# COLORS are now imported from dashboard.ui_config above

# ============================================================================
# MODULE AVAILABILITY DETECTION
# ============================================================================
MODULE_STATUS = {}

# Data Loader
try:
    from modules.shared.data_loader import (
        get_stock_data, get_liquid_stocks, get_stock_name,
        get_current_price, get_all_stocks, get_stock_summary,
        load_full_dataset
    )
    MODULE_STATUS['data_loader'] = True
except Exception as e:
    MODULE_STATUS['data_loader'] = False
    print(f"Data Loader Error: {e}")

# Forecasting
try:
    from modules.forecasting.predict import predict_next_days, get_trend_analysis
    MODULE_STATUS['forecasting'] = True
except Exception as e:
    MODULE_STATUS['forecasting'] = False
    print(f"Forecasting Error: {e}")

# Sentiment
try:
    from modules.sentiment.analyzer import get_sentiment_score, get_market_sentiment
    MODULE_STATUS['sentiment'] = True
except Exception as e:
    MODULE_STATUS['sentiment'] = False
    print(f"Sentiment Error: {e}")

# Anomaly
try:
    from modules.anomaly.detector import detect_anomalies
    MODULE_STATUS['anomaly'] = True
except Exception as e:
    MODULE_STATUS['anomaly'] = False
    print(f"Anomaly Error: {e}")

# Decision Engine
try:
    from modules.decision.engine import (
        make_recommendation, get_top_recommendations, get_market_summary
    )
    from modules.decision.portfolio import Portfolio
    MODULE_STATUS['decision'] = True
except Exception as e:
    MODULE_STATUS['decision'] = False
    print(f"Decision Error: {e}")

# ============================================================================
# CUSTOM CSS (Centralized UI Configuration)
# ============================================================================
# Inject component styles from ui_config
st.markdown(get_component_styles() + get_rtl_css(), unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
# Language
if 'language' not in st.session_state:
    st.session_state.language = 'fr'
set_language(st.session_state.language)

# Portfolio
if 'portfolio' not in st.session_state:
    if MODULE_STATUS['decision']:
        st.session_state.portfolio = Portfolio(initial_capital=10000.0, name="Mon Portefeuille")
    else:
        st.session_state.portfolio = None

# User Profile (NEW: Managed by onboarding system)
if 'onboarding_completed' not in st.session_state:
    st.session_state.onboarding_completed = False

if 'profile' not in st.session_state:
    st.session_state.profile = 'modere'  # Default

if 'profile_score' not in st.session_state:
    st.session_state.profile_score = 4  # Default moderate score

if 'alert_manager' not in st.session_state:
    try:
        from modules.anomaly.alert_manager import AlertManager
        alert_store_path = Path(__file__).parent.parent / 'data' / 'alert_actions.json'
        manager = AlertManager()
        if alert_store_path.exists():
            manager.load_from_file(str(alert_store_path))
        manager.autosave_path = str(alert_store_path)
        st.session_state.alert_manager = manager
    except Exception:
        st.session_state.alert_manager = None

if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

if 'current_page' not in st.session_state:
    st.session_state.current_page = "Vue d'Ensemble"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300)
def load_stock_list():
    """Load and cache stock list"""
    if MODULE_STATUS['data_loader']:
        try:
            return get_liquid_stocks(min_avg_volume=100, min_days=20)
        except:
            return get_all_stocks()[:50]
    return []

@st.cache_data(ttl=300)
def get_cached_stock_data(stock_code, days=60):
    """Load and cache stock historical data"""
    if MODULE_STATUS['data_loader']:
        try:
            df = get_stock_data(stock_code)
            return df.tail(days)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def safe_module_call(func, *args, **kwargs):
    """Safely call module function with error handling"""
    try:
        return func(*args, **kwargs), None
    except Exception as e:
        return None, str(e)

def format_currency(value, symbol="TND"):
    """Format number as currency"""
    if value is None:
        return "N/A"
    return f"{value:,.2f} {symbol}"

def format_percentage(value, with_sign=True):
    """Format number as percentage"""
    if value is None:
        return "N/A"
    if with_sign:
        return f"{value:+.2f}%"
    return f"{value:.2f}%"

def get_recommendation_color(rec):
    """Get color for recommendation"""
    colors = {'BUY': COLORS['buy'], 'SELL': COLORS['sell'], 'HOLD': COLORS['hold']}
    return colors.get(rec, COLORS['neutral'])

def get_recommendation_emoji(rec):
    """Get emoji for recommendation"""
    emojis = {'BUY': '🟢', 'SELL': '🔴', 'HOLD': '🟡'}
    return emojis.get(rec, '⚪')

def get_confidence_emoji(confidence):
    """Get emoji based on confidence level"""
    if confidence >= 0.8:
        return '🔥'
    elif confidence >= 0.7:
        return '⭐'
    elif confidence >= 0.6:
        return '✨'
    return '💫'

def create_price_chart(df, predictions=None, title="Historique des Prix"):
    """Create an interactive price chart with optional predictions"""
    fig = go.Figure()

    # Historical prices
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        mode='lines',
        name='Prix Historique',
        line=dict(color=COLORS['primary'], width=2),
        hovertemplate='%{x}<br>Prix: %{y:.2f} TND<extra></extra>'
    ))

    # Add predictions if available
    if predictions and len(predictions) > 0:
        pred_dates = [p.get('date') or p.get('ds') for p in predictions]
        pred_values = [p.get('predicted_close') or p.get('yhat') for p in predictions]

        # Connect last historical point to first prediction
        last_date = df['date'].iloc[-1]
        last_price = df['close'].iloc[-1]

        fig.add_trace(go.Scatter(
            x=[last_date] + pred_dates,
            y=[last_price] + pred_values,
            mode='lines+markers',
            name='Prévision',
            line=dict(color=COLORS['warning'], width=2, dash='dash'),
            marker=dict(size=8, symbol='diamond'),
            hovertemplate='%{x}<br>Prévu: %{y:.2f} TND<extra></extra>'
        ))

    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="Prix (TND)",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        margin=dict(l=50, r=50, t=50, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def create_sentiment_gauge(score, title="Score de Sentiment"):
    """Create a sentiment gauge chart"""
    # Determine color based on score
    if score > 0.3:
        color = COLORS['success']
    elif score < -0.3:
        color = COLORS['danger']
    else:
        color = COLORS['neutral']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 16}},
        number={'suffix': '', 'font': {'size': 40}},
        gauge={
            'axis': {'range': [-1, 1], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': 'white',
            'borderwidth': 2,
            'bordercolor': '#e0e0e0',
            'steps': [
                {'range': [-1, -0.4], 'color': '#ffebee'},
                {'range': [-0.4, 0.4], 'color': '#f5f5f5'},
                {'range': [0.4, 1], 'color': '#e8f5e9'}
            ],
            'threshold': {
                'line': {'color': '#333', 'width': 2},
                'thickness': 0.75,
                'value': score
            }
        }
    ))

    fig.update_layout(
        height=250,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig

def create_allocation_chart(allocation_dict):
    """Create portfolio allocation pie chart"""
    labels = list(allocation_dict.keys())
    values = list(allocation_dict.values())

    # Custom colors
    colors = [COLORS['primary'], COLORS['success'], COLORS['warning'],
              COLORS['info'], COLORS['danger'], COLORS['neutral']]

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors[:len(labels)]),
        textinfo='label+percent',
        textposition='outside',
        hovertemplate='%{label}<br>%{value:.1f}%<extra></extra>'
    )])

    fig.update_layout(
        title="Allocation du Portefeuille",
        height=350,
        margin=dict(l=20, r=20, t=50, b=20),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2)
    )

    return fig

def create_anomaly_score_gauge(score):
    """Create anomaly score gauge"""
    # Determine color
    if score >= 7:
        color = COLORS['danger']
    elif score >= 3:
        color = COLORS['warning']
    else:
        color = COLORS['success']

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Score d'Anomalie", 'font': {'size': 14}},
        number={'font': {'size': 36}},
        gauge={
            'axis': {'range': [0, 10], 'tickwidth': 1},
            'bar': {'color': color},
            'bgcolor': 'white',
            'steps': [
                {'range': [0, 3], 'color': '#e8f5e9'},
                {'range': [3, 7], 'color': '#fff3e0'},
                {'range': [7, 10], 'color': '#ffebee'}
            ]
        }
    ))

    fig.update_layout(height=200, margin=dict(l=20, r=20, t=30, b=10))
    return fig

def create_signal_breakdown_chart(signals):
    """Create horizontal bar chart for signal breakdown"""
    signal_names = []
    signal_values = []
    signal_colors = []

    if 'forecast' in signals:
        forecast = signals['forecast']
        direction = forecast.get('direction', 'stable')
        magnitude = forecast.get('magnitude', 0) * 100
        signal_names.append('Prévision (40%)')
        signal_values.append(magnitude if direction == 'up' else -magnitude if direction == 'down' else 0)
        signal_colors.append(COLORS['success'] if direction == 'up' else COLORS['danger'] if direction == 'down' else COLORS['neutral'])

    if 'sentiment' in signals:
        sentiment = signals['sentiment']
        score = sentiment.get('score', 0) * 100
        signal_names.append('Sentiment (30%)')
        signal_values.append(score)
        signal_colors.append(COLORS['success'] if score > 0 else COLORS['danger'] if score < 0 else COLORS['neutral'])

    if 'anomaly' in signals:
        anomaly = signals['anomaly']
        detected = anomaly.get('detected', False)
        signal_names.append('Anomalies (20%)')
        signal_values.append(-50 if detected else 25)
        signal_colors.append(COLORS['danger'] if detected else COLORS['success'])

    if 'technical' in signals:
        technical = signals['technical']
        rsi = technical.get('rsi', 50)
        if rsi < 30:
            val = 25
            col = COLORS['success']
        elif rsi > 70:
            val = -25
            col = COLORS['danger']
        else:
            val = 0
            col = COLORS['neutral']
        signal_names.append('Technique (10%)')
        signal_values.append(val)
        signal_colors.append(col)

    fig = go.Figure(go.Bar(
        y=signal_names,
        x=signal_values,
        orientation='h',
        marker_color=signal_colors,
        text=[f"{v:+.1f}" for v in signal_values],
        textposition='outside'
    ))

    fig.update_layout(
        title="Contribution des Signaux",
        xaxis_title="Impact sur le Score",
        height=250,
        margin=dict(l=120, r=50, t=40, b=40),
        xaxis=dict(range=[-100, 100], zeroline=True, zerolinewidth=2)
    )

    return fig

# ============================================================================
# SIDEBAR
# ============================================================================
def render_sidebar():
    """Render the sidebar"""
    with st.sidebar:
        # Logo and title
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1 style='color: #0066CC; margin: 0;'>🏦 BVMT</h1>
            <p style='color: #6C757D; margin: 0; font-size: 0.9rem;'>{t('app.subtitle')}</p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # Language Selector
        st.markdown(f"**🌐 {t('settings.language')}**")
        lang = render_language_selector('language')
        if lang != st.session_state.language:
            st.session_state.language = lang
            st.rerun()

        st.markdown("---")

        # Module status
        st.markdown(f"**📊 {t('modules.status')}**")

        modules = [
            (t('modules.data'), MODULE_STATUS.get('data_loader', False)),
            (t('modules.forecast'), MODULE_STATUS.get('forecasting', False)),
            (t('modules.sentiment'), MODULE_STATUS.get('sentiment', False)),
            (t('modules.anomaly'), MODULE_STATUS.get('anomaly', False)),
            (t('modules.decision'), MODULE_STATUS.get('decision', False)),
        ]

        for name, status in modules:
            emoji = "✅" if status else "❌"
            st.markdown(f"<span style='font-size: 0.85rem;'>{emoji} {name}</span>", unsafe_allow_html=True)

        # Market Memory status badge
        if MARKET_MEMORY_AVAILABLE:
            render_memory_status_badge()

        st.markdown("---")

        # Navigation
        st.markdown(f"**📍 {t('settings.title')}**")
        
        nav_options = [
            f"📊 {t('nav.overview')}", 
            f"🔍 {t('nav.analysis')}", 
            f"💼 {t('nav.portfolio')}", 
            f"⚠️ {t('nav.alerts')}"
        ]
        
        page = st.radio(
            "Navigation",
            nav_options,
            label_visibility="collapsed"
        )
        st.session_state.current_page = page

        st.markdown("---")

        # User profile display (NEW: Uses onboarding system)
        st.markdown(f"**👤 {t('settings.profile')}**")
        
        if ONBOARDING_AVAILABLE:
            user_profile_data = get_user_profile()
            if user_profile_data:
                profile_key = user_profile_data['key']
                profile_emoji = user_profile_data['emoji']
                profile_name = user_profile_data['name']
                profile_score = user_profile_data['score']
                
                # Display profile with color
                profile_color = PROFILES[profile_key]['color']
                st.markdown(
                    f"<div style='background: {profile_color}15; padding: 0.8rem; "
                    f"border-radius: 6px; border-left: 3px solid {profile_color};'>"
                    f"<div style='font-size: 1.1rem; font-weight: 600;'>{profile_emoji} {profile_name}</div>"
                    f"<div style='font-size: 0.75rem; color: #6C757D; margin-top: 0.3rem;'>"
                    f"Score de risque : {profile_score}/8</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            else:
                st.info("Profil : Modéré (par défaut)")
        else:
            # Fallback if onboarding not available
            st.info(f"**{get_profile_name('modere')}**")
        
        # Option to retake questionnaire
        if ONBOARDING_AVAILABLE and st.button("🔄 Refaire le questionnaire", width='stretch'):
            reset_onboarding()
            st.rerun()
        
        # Reset portfolio button
        if st.button(f"🔄 {t('settings.reset_portfolio')}", width='stretch'):
            if MODULE_STATUS['decision']:
                st.session_state.portfolio = Portfolio(initial_capital=10000.0, name="Mon Portefeuille")
                st.success(t('settings.reset_success'))
                st.rerun()

        st.markdown("---")
        
        # Disclaimers
        st.markdown(f"""
        <div style='font-size: 0.75rem; color: #6C757D; padding: 0.5rem 0;'>
            {t('disclaimer.daily_data')}<br><br>
            {t('disclaimer.historical')}<br><br>
            {t('disclaimer.simulation')}
        </div>
        """, unsafe_allow_html=True)

        # Team footer
        st.markdown(f"""
        <div class='team-footer'>
            <p style='font-weight: 600;'>IHEC CODELAB 2.0</p>
            <p style='margin: 0.3rem 0;'>{t('app.team')}</p>
            <p style='margin-top: 0.8rem; font-size: 0.75rem;'>{t('app.made_with')}</p>
        </div>
        """, unsafe_allow_html=True)

    return page

# ============================================================================
# PAGE 1: VUE D'ENSEMBLE (MARKET OVERVIEW)
# ============================================================================
def render_overview_page():
    """Render the market overview page"""
    # Header
    st.markdown("<h1 class='main-header'>📊 Vue d'Ensemble du Marché</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Tableau de bord intelligent pour le marché BVMT</p>", unsafe_allow_html=True)

    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)

    # Get market summary if available
    if MODULE_STATUS['decision']:
        with st.spinner("Analyse du marché..."):
            summary, error = safe_module_call(get_market_summary, st.session_state.profile)
    else:
        summary = None
        error = "Module non disponible"

    # Metric 1: Market Sentiment
    with col1:
        if summary:
            sentiment = summary.get('overall_sentiment', 'NEUTRE')
            emoji = '📈' if sentiment == 'HAUSSIER' else '📉' if sentiment == 'BAISSIER' else '➡️'
            st.metric(
                label="Tendance Marché",
                value=sentiment,
                delta=f"{emoji} {summary.get('buy_signals', 0)} signaux achat"
            )
        else:
            st.metric(label="Tendance Marché", value="N/A", delta="En attente...")

    # Metric 2: Total Stocks Analyzed
    with col2:
        if summary:
            st.metric(
                label="Valeurs Analysées",
                value=summary.get('total_analyzed', 0),
                delta=f"{summary.get('buy_signals', 0)} BUY / {summary.get('sell_signals', 0)} SELL"
            )
        else:
            st.metric(label="Valeurs Analysées", value="N/A")

    # Metric 3: Alerts
    with col3:
        if summary:
            num_alerts = len(summary.get('alerts', []))
            st.metric(
                label="Alertes Actives",
                value=num_alerts,
                delta="Voir détails ⚠️" if num_alerts > 0 else "Aucune alerte ✅"
            )
        else:
            st.metric(label="Alertes", value="N/A")

    # Metric 4: Portfolio Value
    with col4:
        if st.session_state.portfolio:
            try:
                # Get current prices for portfolio
                holdings = st.session_state.portfolio.holdings
                current_prices = {}
                for code in holdings.keys():
                    if MODULE_STATUS['data_loader']:
                        current_prices[code] = get_current_price(code)
                    else:
                        current_prices[code] = holdings[code]['avg_price']

                metrics = st.session_state.portfolio.get_performance_metrics(current_prices)
                st.metric(
                    label="Valeur Portfolio",
                    value=f"{metrics['total_value']:,.0f} TND",
                    delta=f"{metrics['roi_percentage']:+.1f}%"
                )
            except:
                st.metric(label="Valeur Portfolio", value="10,000 TND", delta="0%")
        else:
            st.metric(label="Valeur Portfolio", value="N/A")

    st.markdown("---")

    # Top Recommendations Section
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🟢 Top Recommandations d'Achat")

        if summary and summary.get('top_buys'):
            for rec in summary['top_buys'][:5]:
                conf_emoji = get_confidence_emoji(rec.get('confidence', 0))
                st.markdown(f"""
                <div class='stock-card'>
                    <div>
                        <strong>{rec.get('stock_name', 'N/A')}</strong><br>
                        <small style='color: #666;'>{rec.get('stock_code', '')}</small>
                    </div>
                    <div style='text-align: right;'>
                        <span class='rec-buy' style='font-size: 0.8rem; padding: 0.3rem 0.8rem;'>ACHETER</span><br>
                        <small>{rec.get('confidence', 0):.0%} {conf_emoji}</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune recommandation d'achat disponible")

    with col2:
        st.markdown("### 🔴 Alertes de Vente")

        if summary and summary.get('top_sells'):
            for rec in summary['top_sells'][:5]:
                conf_emoji = get_confidence_emoji(rec.get('confidence', 0))
                st.markdown(f"""
                <div class='stock-card'>
                    <div>
                        <strong>{rec.get('stock_name', 'N/A')}</strong><br>
                        <small style='color: #666;'>{rec.get('stock_code', '')}</small>
                    </div>
                    <div style='text-align: right;'>
                        <span class='rec-sell' style='font-size: 0.8rem; padding: 0.3rem 0.8rem;'>VENDRE</span><br>
                        <small>{abs(rec.get('confidence', 0)):.0%} ⚠️</small>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Aucune alerte de vente active")

    st.markdown("---")

    # Suggested Portfolio Section
    st.markdown("### 💡 Portefeuille Suggéré pour Votre Profil")
    
    # Get current profile display
    if ONBOARDING_AVAILABLE:
        user_profile_data = get_user_profile()
        if user_profile_data:
            profile_display = user_profile_data['display_name']
        else:
            profile_display = '⚖️ Modéré'
    else:
        profile_display = '⚖️ Modéré'
    
    st.write(f"Profil actuel: {profile_display}")

    if 'portfolio_suggestions' not in st.session_state:
        st.session_state.portfolio_suggestions = []

    generate_clicked = st.button("🎯 Générer un Portefeuille Diversifié")

    optimizer_available = True
    try:
        from modules.decision.portfolio_optimizer import suggest_diversified_portfolio
    except Exception:
        optimizer_available = False

    if generate_clicked:
        if not optimizer_available:
            st.info("Module d'optimisation non disponible pour le moment.")
        else:
            capital = 10000.0
            if st.session_state.portfolio:
                try:
                    holdings = st.session_state.portfolio.holdings
                    current_prices = {}
                    for code in holdings.keys():
                        if MODULE_STATUS['data_loader']:
                            current_prices[code] = get_current_price(code)
                        else:
                            current_prices[code] = holdings[code]['avg_price']
                    metrics = st.session_state.portfolio.get_performance_metrics(current_prices)
                    capital = float(metrics.get('total_value', capital))
                except Exception:
                    capital = 10000.0

            st.session_state.portfolio_suggestions = suggest_diversified_portfolio(
                st.session_state.profile, capital
            )

    suggestions = st.session_state.portfolio_suggestions
    if suggestions:
        total_pct = sum(s.get('percentage', 0) for s in suggestions)
        st.caption(f"Allocation totale: {total_pct:.1f}%")

        with st.expander("Voir le détail du portefeuille suggéré", expanded=True):
            for item in suggestions:
                item_type = item.get('type')
                color = "#2ca02c" if item_type == 'STOCK' else "#1f77b4" if item_type == 'BONDS' else "#7f7f7f"
                label = "Action" if item_type == 'STOCK' else "Obligations" if item_type == 'BONDS' else "Cash"
                pct = item.get('percentage', 0)

                st.markdown(
                    f"""
                    <div style='border-left: 4px solid {color}; padding-left: 10px; margin-bottom: 0.5rem;'>
                        <strong>{label}</strong> — {item.get('description', '')}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.progress(min(max(pct / 100, 0), 1.0))

                if item_type == 'STOCK':
                    qty = item.get('quantity', 0) or 0
                    amount = item.get('amount', 0.0) or 0.0
                    price = (amount / qty) if qty > 0 else 0.0
                    st.write(
                        f"**{item.get('stock_name', 'N/A')}** ({item.get('stock_code', '')}) — "
                        f"Quantité: {qty} | Prix: {price:.3f} TND | "
                        f"Montant: {amount:,.2f} TND | {pct:.1f}%"
                    )
                else:
                    st.write(
                        f"Montant: {item.get('amount', 0.0):,.2f} TND | {pct:.1f}%"
                    )

            st.markdown("---")
            st.warning("Cette suggestion est basée sur votre profil. Consultez un conseiller financier.")

            execute_clicked = st.button("✅ Exécuter Toutes les Positions")
            if execute_clicked:
                if not st.session_state.portfolio:
                    st.error("Portefeuille non initialisé")
                else:
                    for item in suggestions:
                        if item.get('type') != 'STOCK':
                            continue
                        code = item.get('stock_code')
                        qty = int(item.get('quantity', 0) or 0)
                        if not code or qty <= 0:
                            continue
                        price = get_current_price(code) if MODULE_STATUS['data_loader'] else 0.0
                        if price <= 0:
                            st.error(f"Prix indisponible pour {code}")
                            continue
                        result = st.session_state.portfolio.buy(code, get_stock_name(code), price, qty)
                        if result.get('success'):
                            st.success(result.get('message', 'Achat effectué'))
                        else:
                            st.error(result.get('message', "Erreur lors de l'achat"))
                    st.rerun()

    elif generate_clicked and optimizer_available:
        st.info("Aucune suggestion disponible pour le moment.")

    # Market Distribution Chart
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### 📊 Distribution des Signaux")
        if summary:
            labels = ['Achat', 'Vente', 'Conserver']
            values = [
                summary.get('buy_signals', 0),
                summary.get('sell_signals', 0),
                summary.get('hold_signals', 0)
            ]
            colors = [COLORS['buy'], COLORS['sell'], COLORS['hold']]

            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                marker=dict(colors=colors),
                textinfo='value+percent',
                textposition='inside'
            )])
            fig.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=20, b=20),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.1)
            )
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("Graphique non disponible")

    with col2:
        st.markdown("### 📢 Alertes Récentes")
        if summary and summary.get('alerts'):
            for alert in summary['alerts'][:5]:
                if 'Anomalie' in alert:
                    st.warning(f"⚠️ {alert}")
                elif 'Signal fort' in alert:
                    if 'BUY' in alert:
                        st.success(f"🟢 {alert}")
                    else:
                        st.error(f"🔴 {alert}")
                else:
                    st.info(f"ℹ️ {alert}")
        else:
            st.success("✅ Aucune alerte - Marché calme")

# ============================================================================
# PAGE 2: ANALYSE VALEUR (STOCK ANALYSIS)
# ============================================================================
def render_analysis_page():
    """Render the stock analysis page"""
    st.markdown("<h1 class='main-header'>🔍 Analyse de Valeur</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Analyse approfondie d'une valeur boursière</p>", unsafe_allow_html=True)

    # Stock selector
    stock_list = load_stock_list()

    if not stock_list:
        st.error("Impossible de charger la liste des valeurs. Vérifiez que le module data_loader est disponible.")
        return

    # Create display options
    stock_options = {code: f"{get_stock_name(code)} ({code})" for code in stock_list}

    selected_code = st.selectbox(
        "Sélectionnez une valeur",
        options=list(stock_options.keys()),
        format_func=lambda x: stock_options.get(x, x),
        key='stock_selector'
    )

    if not selected_code:
        return

    st.session_state.selected_stock = selected_code
    stock_name = get_stock_name(selected_code)

    # Current Price Header
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    if MODULE_STATUS['data_loader']:
        summary = get_stock_summary(selected_code)
        with col1:
            current_price = summary.get('current_price', 0)
            change = summary.get('change_pct', 0)
            st.metric(
                label="Prix Actuel",
                value=f"{current_price:.2f} TND",
                delta=f"{change:+.2f}%"
            )

        with col2:
            avg_vol = summary.get('avg_volume_30d', 0)
            st.metric(
                label="Volume Moyen (30j)",
                value=f"{avg_vol:,.0f}",
                delta=None
            )

        with col3:
            date_range = summary.get('date_range', 'N/A')
            st.metric(
                label="Période de Données",
                value=summary.get('num_data_points', 0),
                delta=f"jours"
            )

    # Tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Prévision", "📰 Sentiment", "⚠️ Anomalies", "💡 Recommandation"])

    # TAB 1: FORECASTING
    with tab1:
        st.markdown("### 📈 Prévision des Prix")

        if MODULE_STATUS['forecasting']:
            with st.spinner("Calcul des prévisions..."):
                forecast, error = safe_module_call(predict_next_days, selected_code, 5)

            if forecast and not error:
                # Price chart with predictions
                historical_df = get_cached_stock_data(selected_code, days=60)

                if not historical_df.empty:
                    predictions = forecast.get('predictions', [])
                    fig = create_price_chart(historical_df, predictions,
                                            f"Historique et Prévision - {stock_name}")
                    st.plotly_chart(fig, width='stretch')

                # Predictions table
                st.markdown("#### Prévisions pour les 5 prochains jours")
                if forecast.get('predictions'):
                    pred_df = pd.DataFrame(forecast['predictions'])
                    # Select only the columns we need
                    if 'ds' in pred_df.columns and 'yhat' in pred_df.columns:
                        display_df = pred_df[['ds', 'yhat']].copy()
                        display_df.columns = ['Date', 'Prix Prévu (TND)']
                        st.dataframe(display_df, width='stretch', hide_index=True)
                    else:
                        st.dataframe(pred_df, width='stretch', hide_index=True)

                # Model metrics
                st.markdown("#### Métriques du Modèle")
                metrics = forecast.get('metrics', {})
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("RMSE", f"{metrics.get('rmse', 0):.2f} TND")
                with col2:
                    st.metric("MAE", f"{metrics.get('mae', 0):.2f} TND")
                with col3:
                    st.metric("Précision Directionnelle", f"{metrics.get('directional_accuracy', 0):.0%}")

                st.caption(f"Modèle utilisé: {forecast.get('model_used', 'N/A')}")
            else:
                st.error(f"Erreur de prévision: {error}")
        else:
            st.warning("⚠️ Module de prévision non disponible")
            # Show historical data only
            historical_df = get_cached_stock_data(selected_code, days=60)
            if not historical_df.empty:
                fig = create_price_chart(historical_df, None, f"Historique - {stock_name}")
                st.plotly_chart(fig, width='stretch')

    # TAB 2: SENTIMENT
    with tab2:
        st.markdown("### 📰 Analyse de Sentiment")

        if MODULE_STATUS['sentiment']:
            with st.spinner("Analyse du sentiment..."):
                sentiment, error = safe_module_call(get_sentiment_score, selected_code)

            if sentiment and not error:
                col1, col2 = st.columns([1, 1])

                with col1:
                    # Sentiment gauge
                    score = sentiment.get('sentiment_score', 0)
                    fig = create_sentiment_gauge(score)
                    st.plotly_chart(fig, width='stretch')

                with col2:
                    # Metrics
                    st.metric("Score de Sentiment", f"{score:.2f}")
                    st.metric("Articles Analysés", sentiment.get('num_articles', 0))

                    # Classification emoji
                    if score > 0.3:
                        st.success("😊 Sentiment Positif")
                    elif score < -0.3:
                        st.error("😟 Sentiment Négatif")
                    else:
                        st.info("😐 Sentiment Neutre")

                # Summary
                st.markdown("#### Résumé")
                st.info(sentiment.get('summary', 'Aucun résumé disponible'))

                # Headlines
                headlines = sentiment.get('sample_headlines', [])
                if headlines:
                    st.markdown("#### Articles Récents")
                    for article in headlines[:5]:
                        emoji = '✅' if article.get('sentiment', 0) > 0.2 else '❌' if article.get('sentiment', 0) < -0.2 else '⚪'
                        st.markdown(f"""
                        <div class='alert-info'>
                            {emoji} <strong>{article.get('headline', 'N/A')}</strong><br>
                            <small>Source: {article.get('source', 'N/A')} | {article.get('date', '')} |
                            Sentiment: {article.get('sentiment', 0):.2f}</small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning(f"Erreur d'analyse: {error}")
        else:
            st.warning("⚠️ Module de sentiment non disponible")
            st.info("Le sentiment serait analysé à partir des actualités financières tunisiennes.")

    # TAB 3: ANOMALIES
    with tab3:
        st.markdown("### ⚠️ Détection d'Anomalies")

        if MODULE_STATUS['anomaly']:
            with st.spinner("Analyse des anomalies..."):
                anomalies, error = safe_module_call(detect_anomalies, selected_code, 30)

            if anomalies and not error:
                # Risk level banner
                risk_level = anomalies.get('risk_level', 'NORMAL')
                if risk_level == 'HIGH':
                    st.error("🔴 RISQUE ÉLEVÉ: Anomalies critiques détectées - Prudence requise!")
                elif risk_level == 'ELEVATED':
                    st.warning("🟡 RISQUE MODÉRÉ: Anomalies mineures détectées")
                else:
                    st.success("🟢 NORMAL: Aucune anomalie critique détectée")

                col1, col2 = st.columns([1, 1])

                with col1:
                    # Anomaly score gauge
                    score = anomalies.get('score', 0)
                    fig = create_anomaly_score_gauge(score)
                    st.plotly_chart(fig, width='stretch')

                with col2:
                    st.metric("Score d'Anomalie", f"{score:.1f} / 10")
                    st.metric("Niveau de Risque", risk_level)

                # Summary
                st.markdown("#### Résumé")
                st.info(anomalies.get('summary', 'Aucun résumé disponible'))

                # Detected anomalies list
                detected = anomalies.get('anomalies_detected', [])
                if detected:
                    st.markdown("#### Anomalies Détectées")
                    for anom in detected[:10]:
                        severity = anom.get('severity', 'LOW')
                        if severity == 'HIGH':
                            css_class = 'alert-critical'
                            emoji = '🔴'
                        elif severity == 'MEDIUM':
                            css_class = 'alert-warning'
                            emoji = '🟡'
                        else:
                            css_class = 'alert-info'
                            emoji = '🟢'

                        st.markdown(f"""
                        <div class='{css_class}'>
                            {emoji} <strong>{anom.get('type', 'N/A').upper()}</strong> ({severity})<br>
                            📅 {anom.get('date', 'N/A')}<br>
                            {anom.get('description', 'N/A')}
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.success("✅ Aucune anomalie détectée - Trading normal")
            else:
                st.warning(f"Erreur d'analyse: {error}")
        else:
            st.warning("⚠️ Module d'anomalies non disponible")

    # TAB 4: RECOMMENDATION
    with tab4:
        st.markdown("### 💡 Recommandation")

        if MODULE_STATUS['decision']:
            with st.spinner("Génération de la recommandation..."):
                recommendation, error = safe_module_call(
                    make_recommendation,
                    selected_code,
                    st.session_state.profile
                )

            if recommendation and not error:
                rec = recommendation.get('recommendation', 'HOLD')
                confidence = recommendation.get('confidence', 0)

                # Big recommendation display
                rec_class = f"rec-{rec.lower()}"
                rec_text = "ACHETER" if rec == "BUY" else "VENDRE" if rec == "SELL" else "CONSERVER"

                st.markdown(f"""
                <div style='text-align: center; padding: 2rem; background: #f8f9fa; border-radius: 16px; margin: 1rem 0;'>
                    <p style='color: #666; margin-bottom: 0.5rem;'>RECOMMANDATION</p>
                    <span class='{rec_class}'>{rec_text}</span>
                    <p style='margin-top: 1rem; font-size: 1.2rem;'>
                        Confiance: <strong>{confidence:.0%}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Key metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Score", f"{recommendation.get('score', 0):.1f} / 10")
                with col2:
                    st.metric("Confiance", f"{confidence:.0%}")
                with col3:
                    st.metric("Risque", recommendation.get('risk_level', 'N/A'))

                # Technical indicators
                st.markdown("#### 📊 Indicateurs Techniques")
                technical_data = recommendation.get('signals', {}).get('technical', {})
                rsi_value = technical_data.get('rsi')
                macd_data = technical_data.get('macd')

                if rsi_value is None or macd_data is None:
                    st.info("Données insuffisantes pour les indicateurs techniques")
                else:
                    col_left, col_right = st.columns(2)

                    with col_left:
                        fig = go.Figure(go.Indicator(
                            mode="gauge+number",
                            value=rsi_value,
                            domain={'x': [0, 1], 'y': [0, 1]},
                            title={'text': "RSI (14 jours)", 'font': {'size': 14}},
                            number={'font': {'size': 32}},
                            gauge={
                                'axis': {'range': [0, 100], 'tickwidth': 1},
                                'bar': {'color': COLORS['primary']},
                                'bgcolor': 'white',
                                'steps': [
                                    {'range': [0, 30], 'color': '#d8f3dc'},   # light green
                                    {'range': [30, 70], 'color': '#eeeeee'},  # light gray
                                    {'range': [70, 100], 'color': '#f8d7da'}  # light coral
                                ]
                            }
                        ))
                        fig.update_layout(height=220, margin=dict(l=20, r=20, t=30, b=10))
                        st.plotly_chart(fig, width='stretch')

                    with col_right:
                        macd_value = macd_data.get('macd')
                        signal_value = macd_data.get('signal')
                        trend = macd_data.get('trend', 'bearish')
                        trend_label = "HAUSSIER" if trend == 'bullish' else "BAISSIER"
                        trend_delta = "+1" if trend == 'bullish' else "-1"

                        st.metric("MACD", f"{macd_value:.4f}")
                        st.metric("Signal", f"{signal_value:.4f}")
                        st.metric("Tendance", trend_label, delta=trend_delta)

                # Signal breakdown chart
                signals = recommendation.get('signals', {})
                if signals:
                    fig = create_signal_breakdown_chart(signals)
                    st.plotly_chart(fig, width='stretch')

                # EXPLAIN BUTTON - THE STAR FEATURE
                st.markdown("---")
                with st.expander("💡 **POURQUOI CETTE RECOMMANDATION?** (Cliquez pour voir l'explication détaillée)", expanded=False):
                    st.markdown("""
                    <div class='explanation-box'>
                    """, unsafe_allow_html=True)

                    explanation = recommendation.get('explanation', 'Explication non disponible')
                    st.code(explanation, language=None)

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Signal details
                    st.markdown("#### 📊 Détail des Signaux")

                    for signal_name, signal_data in signals.items():
                        if isinstance(signal_data, dict) and 'error' not in signal_data:
                            with st.expander(f"📌 {signal_name.upper()}"):
                                for key, value in signal_data.items():
                                    if key != 'headlines' and key != 'predictions':
                                        st.write(f"**{key}**: {value}")

                    # Suggested action
                    st.markdown("---")
                    st.markdown("#### 💰 Action Suggérée")
                    st.info(recommendation.get('suggested_action', 'Aucune action suggérée'))

                    # Disclaimer
                    st.warning("""
                    ⚠️ **AVERTISSEMENT**: Cette recommandation est basée sur une analyse quantitative automatisée.
                    Elle ne constitue pas un conseil en investissement. Consultez toujours un conseiller
                    financier professionnel avant de prendre des décisions d'investissement.
                    """)

                # Portfolio action section
                st.markdown("---")
                st.markdown("#### 💼 Ajouter au Portefeuille")

                current_price = recommendation.get('current_price', 0)

                col1, col2 = st.columns([2, 1])

                with col1:
                    quantity = st.number_input(
                        "Quantité d'actions",
                        min_value=1,
                        max_value=1000,
                        value=50,
                        step=10
                    )
                    total_cost = quantity * current_price
                    st.write(f"**Coût estimé:** {total_cost:,.2f} TND")

                with col2:
                    st.write("")  # Spacing
                    st.write("")

                    if rec == 'BUY':
                        if st.button("🟢 Acheter", type="primary", width='stretch'):
                            if st.session_state.portfolio:
                                result = st.session_state.portfolio.buy(
                                    selected_code, stock_name, current_price, quantity
                                )
                                if result['success']:
                                    st.success(result['message'])
                                else:
                                    st.error(result['message'])
                            else:
                                st.error("Portfolio non initialisé")

                    if rec == 'SELL':
                        if st.button("🔴 Vendre", type="primary", width='stretch'):
                            if st.session_state.portfolio:
                                result = st.session_state.portfolio.sell(
                                    selected_code, current_price, quantity
                                )
                                if result['success']:
                                    st.success(result['message'])
                                else:
                                    st.error(result['message'])
                            else:
                                st.error("Portfolio non initialisé")
            else:
                st.error(f"Erreur: {error}")
        else:
            st.warning("⚠️ Module de décision non disponible")
    
    # ========================================================================
    # MARKET MEMORY: Semantic Search & Evidence
    # ========================================================================
    if MARKET_MEMORY_AVAILABLE:
        st.markdown("---")
        render_memory_search_widget(
            placeholder=f"Questions sur {stock_name} ou le marché...",
            default_collection='bvmt_news',
            filters={'ticker': selected_code} if selected_code else None
        )
        
        # Show evidence for current stock
        st.markdown("### 🧠 Mémoire du Marché - Evidence")
        st.caption(f"Contexte sémantique retrouvé pour {stock_name}")
        
        evidence = get_memory_evidence(selected_code, f"analyse {stock_name}")
        
        if evidence:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**📰 Actualités**")
                news_items = evidence.get('news', [])
                if news_items:
                    for item in news_items[:2]:
                        st.caption(f"• {item['text'][:80]}... (Score: {item['score']:.2f})")
                else:
                    st.caption("Aucune actualité")
            
            with col2:
                st.markdown("**⚠️ Anomalies**")
                anomaly_items = evidence.get('anomalies', [])
                if anomaly_items:
                    for item in anomaly_items[:2]:
                        st.caption(f"• {item['text'][:80]}... (Score: {item['score']:.2f})")
                else:
                    st.caption("Aucune anomalie")
            
            with col3:
                st.markdown("**💡 Recommandations**")
                rec_items = evidence.get('recommendations', [])
                if rec_items:
                    for item in rec_items[:2]:
                        st.caption(f"• {item['text'][:80]}... (Score: {item['score']:.2f})")
                else:
                    st.caption("Aucune recommandation")

# ============================================================================
# PAGE 3: MON PORTEFEUILLE (PORTFOLIO)
# ============================================================================
def render_portfolio_page():
    """Render the portfolio page"""
    st.markdown("<h1 class='main-header'>💼 Mon Portefeuille</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='sub-header'>Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>", unsafe_allow_html=True)

    portfolio = st.session_state.portfolio

    if not portfolio:
        st.error("Portefeuille non initialisé. Vérifiez que le module decision est disponible.")
        return

    # Get current prices
    current_prices = {}
    for code in portfolio.holdings.keys():
        if MODULE_STATUS['data_loader']:
            current_prices[code] = get_current_price(code)
        else:
            current_prices[code] = portfolio.holdings[code]['avg_price']

    # Performance metrics
    metrics = portfolio.get_performance_metrics(current_prices)

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_color = "normal" if metrics['roi_percentage'] >= 0 else "inverse"
        st.metric(
            label="Valeur Totale",
            value=f"{metrics['total_value']:,.2f} TND",
            delta=f"{metrics['roi_percentage']:+.2f}%"
        )

    with col2:
        st.metric(
            label="Gain/Perte",
            value=f"{metrics['total_gain_loss']:+,.2f} TND",
            delta=f"Réalisé: {metrics['realized_profit']:+,.2f} TND"
        )

    with col3:
        st.metric(
            label="Liquidités",
            value=f"{metrics['cash']:,.2f} TND",
            delta=f"{(metrics['cash']/metrics['total_value']*100):.1f}% du total"
        )

    with col4:
        st.metric(
            label="Taux de Succès",
            value=f"{metrics['win_rate']:.0f}%",
            delta=f"{metrics['num_closed_trades']} trades clôturés"
        )

    st.markdown("---")

    # Two columns: Positions and Allocation
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📊 Positions Ouvertes")

        positions = portfolio.get_position_details(current_prices)

        if positions:
            # Create DataFrame for display
            pos_data = []
            for pos in positions:
                pos_data.append({
                    'Valeur': pos['stock_name'],
                    'Qté': pos['quantity'],
                    'Prix Moyen': f"{pos['avg_price']:.2f}",
                    'Prix Actuel': f"{pos['current_price']:.2f}",
                    'Valeur': f"{pos['current_value']:,.2f}",
                    'G/P': f"{pos['gain_loss']:+.2f}",
                    'G/P %': f"{pos['gain_loss_pct']:+.1f}%",
                })

            pos_df = pd.DataFrame(pos_data)

            # Style the dataframe
            st.dataframe(
                pos_df,
                width='stretch',
                hide_index=True,
                column_config={
                    'G/P %': st.column_config.TextColumn(
                        'G/P %',
                        help='Gain ou perte en pourcentage'
                    )
                }
            )
        else:
            st.info("📭 Aucune position ouverte. Analysez des valeurs pour commencer à investir!")

    with col2:
        st.markdown("### 🥧 Allocation")

        allocation = portfolio.get_allocation(current_prices)

        if allocation:
            # Rename CASH to French
            allocation_display = {}
            for key, value in allocation.items():
                if key == 'CASH':
                    allocation_display['Liquidités'] = value
                else:
                    allocation_display[get_stock_name(key)] = value

            fig = create_allocation_chart(allocation_display)
            st.plotly_chart(fig, width='stretch')

    st.markdown("---")

    # Transaction History
    st.markdown("### 📜 Historique des Transactions")

    history = portfolio.get_transaction_history(limit=20)

    if history:
        hist_data = []
        for tx in history:
            tx_type = "🟢 ACHAT" if tx['type'] == 'BUY' else "🔴 VENTE"
            hist_data.append({
                'Date': tx['date'],
                'Type': tx_type,
                'Valeur': tx['stock_name'],
                'Quantité': tx['quantity'],
                'Prix': f"{tx['price']:.2f} TND",
                'Total': f"{tx['total']:.2f} TND"
            })

        hist_df = pd.DataFrame(hist_data)
        st.dataframe(hist_df, width='stretch', hide_index=True)
    else:
        st.info("📭 Aucune transaction enregistrée")

    # Quick Actions
    st.markdown("---")
    st.markdown("### ⚡ Actions Rapides")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Analyser Positions", width='stretch'):
            if positions and MODULE_STATUS['decision']:
                st.markdown("#### Analyse des Positions")
                for pos in positions:
                    rec, _ = safe_module_call(make_recommendation, pos['stock_code'], st.session_state.profile)
                    if rec:
                        emoji = get_recommendation_emoji(rec['recommendation'])
                        st.write(f"{emoji} **{pos['stock_name']}**: {rec['recommendation']} ({rec['confidence']:.0%})")

    with col2:
        if st.button("📈 Voir Top Opportunités", width='stretch'):
            if MODULE_STATUS['decision']:
                top_buys, _ = safe_module_call(get_top_recommendations, 3, st.session_state.profile, 'buy')
                if top_buys:
                    st.markdown("#### Top 3 Opportunités")
                    for rec in top_buys:
                        st.success(f"🟢 {rec['stock_name']}: Score {rec['score']:.1f}")

    with col3:
        if st.button("📥 Exporter CSV", width='stretch'):
            if positions:
                pos_df = pd.DataFrame(positions)
                csv = pos_df.to_csv(index=False)
                st.download_button(
                    "Télécharger",
                    csv,
                    "portfolio.csv",
                    "text/csv"
                )

# ============================================================================
# PAGE 4: ALERTES (ALERTS)
# ============================================================================
def render_alerts_page():
    """Render the alerts page"""
    st.markdown("<h1 class='main-header'>⚠️ Alertes et Surveillance</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-header'>Surveillance active des anomalies de marché</p>", unsafe_allow_html=True)

    # Get market summary for alerts
    alerts = []
    critical_count = 0
    warning_count = 0

    if MODULE_STATUS['decision']:
        summary, _ = safe_module_call(get_market_summary, st.session_state.profile)
        if summary:
            alerts = summary.get('alerts', [])
            for alert in alerts:
                if 'Anomalie' in alert:
                    critical_count += 1
                else:
                    warning_count += 1

    # Alert summary banner
    if critical_count > 0:
        st.error(f"⚠️ **{len(alerts)} ALERTES ACTIVES** | 🔴 {critical_count} Critiques | 🟡 {warning_count} Modérées")
    elif warning_count > 0:
        st.warning(f"⚠️ **{len(alerts)} ALERTES ACTIVES** | 🟡 {warning_count} Modérées")
    else:
        st.success("✅ **AUCUNE ALERTE ACTIVE** | Marché calme")

    st.markdown("---")

    # Filters
    filter_choice = st.radio("Filtrer les alertes", ["Toutes", "Non traitées", "Traitées"], horizontal=True)

    # Portfolio Alerts (Priority)
    st.markdown("### 🔔 Alertes sur vos Positions")

    portfolio = st.session_state.portfolio
    if portfolio and portfolio.holdings:
        portfolio_alerts = []

        for stock_code in portfolio.holdings.keys():
            stock_name = get_stock_name(stock_code)

            # Check for anomalies
            if MODULE_STATUS['anomaly']:
                anomaly_result, _ = safe_module_call(detect_anomalies, stock_code, 30)
                if anomaly_result and anomaly_result.get('risk_level') != 'NORMAL':
                    portfolio_alerts.append({
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'type': 'anomaly',
                        'level': anomaly_result.get('risk_level'),
                        'message': anomaly_result.get('summary')
                    })

            # Check for sell signals
            if MODULE_STATUS['decision']:
                rec, _ = safe_module_call(make_recommendation, stock_code, st.session_state.profile)
                if rec and rec.get('recommendation') == 'SELL' and rec.get('confidence', 0) >= 0.7:
                    portfolio_alerts.append({
                        'stock_code': stock_code,
                        'stock_name': stock_name,
                        'type': 'sell_signal',
                        'level': 'HIGH',
                        'message': f"Signal de vente fort ({rec['confidence']:.0%} confiance)"
                    })

        if portfolio_alerts:
            for alert in portfolio_alerts:
                if alert['level'] == 'HIGH':
                    st.markdown(f"""
                    <div class='alert-critical'>
                        🔴 <strong>{alert['stock_name']}</strong><br>
                        {alert['message']}<br>
                        <small>Type: {alert['type']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class='alert-warning'>
                        🟡 <strong>{alert['stock_name']}</strong><br>
                        {alert['message']}<br>
                        <small>Type: {alert['type']}</small>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.success("✅ Aucune alerte sur vos positions")
    else:
        st.info("📭 Aucune position en portefeuille à surveiller")

    st.markdown("---")

    # Market-wide Alerts
    st.markdown("### 🌐 Alertes du Marché")

    manager = st.session_state.get('alert_manager')
    alerts_feed = []

    if manager:
        if filter_choice == "Non traitées":
            alerts_feed = manager.get_unactioned_alerts()
        elif filter_choice == "Traitées":
            alerts_feed = [a for a in manager.alerts if a.get('alert_id') in manager.actions]
        else:
            alerts_feed = manager.alerts

        alerts_feed = sorted(
            alerts_feed,
            key=lambda a: a.get('timestamp') or a.get('date') or "",
            reverse=True
        )

    if alerts_feed:
        for alert in alerts_feed:
            severity = alert.get('severity', 'MEDIUM')
            alert_type = alert.get('type', 'anomaly')
            stock_name = alert.get('stock_name', 'N/A')
            stock_code = alert.get('stock_code', '')
            description = alert.get('description', 'Alerte détectée')

            if severity == 'HIGH':
                css_class = 'alert-critical'
                emoji = '🔴'
            elif severity == 'MEDIUM':
                css_class = 'alert-warning'
                emoji = '🟡'
            else:
                css_class = 'alert-info'
                emoji = '🔵'

            st.markdown(f"""
            <div class='{css_class}'>
                {emoji} <strong>{stock_name}</strong> ({stock_code})<br>
                {description}<br>
                <small>Type: {alert_type} | Sévérité: {severity}</small>
            </div>
            """, unsafe_allow_html=True)

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                if st.button("📊 Analyser", key=f"analyze_{alert.get('alert_id')}"):
                    st.session_state.selected_stock = stock_code
                    st.session_state.current_page = "🔍 Analyse Valeur"
                    st.rerun()

            with col2:
                if st.button("🔕 Ignorer", key=f"ignore_{alert.get('alert_id')}"):
                    manager.record_action(alert.get('alert_id'), 'ignored')
                    st.rerun()

            with col3:
                if st.button("🔍 Enquêter", key=f"investigate_{alert.get('alert_id')}"):
                    manager.record_action(alert.get('alert_id'), 'investigated')
                    st.rerun()

            with col4:
                if st.button("📈 Trader", key=f"trade_{alert.get('alert_id')}"):
                    manager.record_action(alert.get('alert_id'), 'traded')
                    st.session_state.selected_stock = stock_code
                    st.session_state.current_page = "🔍 Analyse Valeur"
                    st.rerun()

            action = manager.actions.get(alert.get('alert_id'))
            if action:
                action_type = action.get('action_type')
                action_ts = action.get('timestamp', '')
                if action_type in ['traded', 'reported']:
                    action_marker = "🟢"
                elif action_type == 'investigated':
                    action_marker = "🔵"
                else:
                    action_marker = "⚪"
                st.caption(f"{action_marker} Action: {action_type} le {action_ts}")

    elif alerts:
        for alert in alerts:
            if 'Anomalie' in alert:
                st.markdown(f"""
                <div class='alert-critical'>
                    🔴 <strong>ANOMALIE DÉTECTÉE</strong><br>
                    {alert}
                </div>
                """, unsafe_allow_html=True)
            elif 'BUY' in alert:
                st.markdown(f"""
                <div class='alert-success'>
                    🟢 <strong>OPPORTUNITÉ</strong><br>
                    {alert}
                </div>
                """, unsafe_allow_html=True)
            elif 'SELL' in alert:
                st.markdown(f"""
                <div class='alert-warning'>
                    🟡 <strong>ATTENTION</strong><br>
                    {alert}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='alert-info'>
                    ℹ️ {alert}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Aucune alerte de marché active")

    st.markdown("---")

    # Historique des Actions
    st.markdown("### 🧾 Historique des Actions")
    if manager:
        with st.expander("Voir l'historique", expanded=False):
            rows = []
            for alert_id, action in manager.actions.items():
                alert = next((a for a in manager.alerts if a.get('alert_id') == alert_id), {})
                rows.append({
                    'Date': action.get('timestamp'),
                    'Valeur': alert.get('stock_name', 'N/A'),
                    "Type d'Alerte": alert.get('type', 'N/A'),
                    'Action Prise': action.get('action_type', 'N/A'),
                    'Notes': action.get('user_notes', '')
                })

            if rows:
                df = pd.DataFrame(rows).sort_values('Date', ascending=False)
                st.dataframe(df, width='stretch')
            else:
                st.info("Aucune action enregistrée pour le moment.")
    else:
        st.info("Gestionnaire d'alertes non disponible.")

    # Alert Statistics
    st.markdown("### 📊 Statistiques")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Alertes Aujourd'hui", len(alerts))

    with col2:
        st.metric("Valeurs Surveillées", len(load_stock_list()))

    with col3:
        st.metric("Positions en Portefeuille", len(portfolio.holdings) if portfolio else 0)

    # Scan button
    st.markdown("---")
    if st.button("🔄 Scanner le Marché", type="primary", width='stretch'):
        with st.spinner("Scan en cours..."):
            stock_list = load_stock_list()[:20]  # Limit to 20 for speed

            progress_bar = st.progress(0)
            anomaly_count = 0

            for i, stock_code in enumerate(stock_list):
                if MODULE_STATUS['anomaly']:
                    result, _ = safe_module_call(detect_anomalies, stock_code, 15)
                    if result and result.get('risk_level') != 'NORMAL':
                        anomaly_count += 1
                        st.warning(f"⚠️ {get_stock_name(stock_code)}: {result.get('summary', 'Anomalie détectée')}")

                progress_bar.progress((i + 1) / len(stock_list))

            if anomaly_count == 0:
                st.success("✅ Scan terminé - Aucune nouvelle anomalie détectée")
            else:
                st.warning(f"⚠️ Scan terminé - {anomaly_count} anomalies trouvées")
    
    # ========================================================================
    # MARKET MEMORY: Similar Anomalies Search
    # ========================================================================
    if MARKET_MEMORY_AVAILABLE and alerts_feed:
        st.markdown("---")
        st.markdown("### 🔎 Recherche de Patterns Similaires")
        st.caption("Utilisez le Market Memory pour trouver des anomalies similaires dans l'historique")
        
        # Select an alert to find similar patterns
        selected_alert_idx = st.selectbox(
            "Sélectionner une alerte pour trouver des patterns similaires",
            options=range(len(alerts_feed)),
            format_func=lambda i: f"[{alerts_feed[i].get('stock_name', 'N/A')}] {alerts_feed[i].get('description', 'Alerte')[:60]}...",
            key='similar_alert_selector'
        )
        
        if selected_alert_idx is not None and selected_alert_idx < len(alerts_feed):
            selected_alert = alerts_feed[selected_alert_idx]
            reference_text = selected_alert.get('description', '')
            
            if reference_text:
                render_similar_items_widget(
                    reference_text=reference_text,
                    collection='bvmt_anomalies',
                    title="🔗 Anomalies Historiques Similaires",
                    top_k=3
                )

# ============================================================================
# MAIN APP
# ============================================================================
def main():
    """Main application entry point"""
    # ════════════════════════════════════════════════════════════════════════
    # ONBOARDING GATE (First-Time User Experience)
    # ════════════════════════════════════════════════════════════════════════
    # Show onboarding if user hasn't completed it yet
    if ONBOARDING_AVAILABLE and should_show_onboarding():
        run_onboarding()
        return  # Exit main until onboarding is complete
    
    # ════════════════════════════════════════════════════════════════════════
    # MAIN DASHBOARD (Post-Onboarding)
    # ════════════════════════════════════════════════════════════════════════
    # Render sidebar and get selected page
    page = render_sidebar()

    # Route to appropriate page based on icon/keyword (language-independent)
    if "📊" in page:
        render_overview_page()
    elif "🔍" in page:
        render_analysis_page()
    elif "💼" in page:
        render_portfolio_page()
    elif "⚠️" in page:
        render_alerts_page()
    else:
        render_overview_page()

if __name__ == "__main__":
    main()
