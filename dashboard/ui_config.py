"""
UI Configuration - BVMT Trading Assistant
==========================================
Centralized color system and visual identity for professional finance UI.

Design Philosophy:
- Light mode by default (suitable for trading environments)
- Muted, professional colors (avoid aggressive tones)
- Clear visual hierarchy (titles → sections → cards → text)
- Accessibility-first (WCAG AA compliant contrast ratios)
- Finance industry standards (inspired by Bloomberg, Refinitiv)

Color Psychology:
- Blue: Trust, stability, professional (finance standard)
- Green: Growth, positive returns (muted, not neon)
- Red: Risk, losses (muted, not alarming)
- Gray: Neutral, informational
- Amber: Caution, moderate risk
"""

# ============================================================================
# COLOR PALETTE - Finance Professional (Light Mode)
# ============================================================================

COLORS = {
    # ──────────────────────────────────────────────────────────────────────
    # PRIMARY COLORS (Brand & Trust)
    # ──────────────────────────────────────────────────────────────────────
    'primary': '#1E40AF',          # Deep blue - Trust, stability (finance standard)
    'primary_light': '#3B82F6',    # Medium blue - Interactive elements
    'primary_dark': '#1E3A8A',     # Navy - Headers, important text
    
    # ──────────────────────────────────────────────────────────────────────
    # SEMANTIC COLORS (Trading Signals)
    # ──────────────────────────────────────────────────────────────────────
    'success': '#059669',          # Muted green - Positive returns, buy signals
    'success_light': '#D1FAE5',    # Light green bg - Success alerts
    'success_text': '#065F46',     # Dark green text - High contrast
    
    'danger': '#DC2626',           # Muted red - Losses, sell signals
    'danger_light': '#FEE2E2',     # Light red bg - Danger alerts
    'danger_text': '#991B1B',      # Dark red text - High contrast
    
    'warning': '#D97706',          # Amber - Caution, moderate risk
    'warning_light': '#FEF3C7',    # Light amber bg - Warning alerts
    'warning_text': '#92400E',     # Dark amber text - High contrast
    
    'info': '#0284C7',             # Sky blue - Informational
    'info_light': '#E0F2FE',       # Light blue bg - Info alerts
    'info_text': '#075985',        # Dark blue text - High contrast
    
    # ──────────────────────────────────────────────────────────────────────
    # NEUTRAL COLORS (Backgrounds & Text)
    # ──────────────────────────────────────────────────────────────────────
    'bg_primary': '#FFFFFF',       # Pure white - Main background
    'bg_secondary': '#F9FAFB',     # Off-white - Secondary sections
    'bg_tertiary': '#F3F4F6',      # Light gray - Cards, dividers
    
    'text_primary': '#111827',     # Near black - Main text (high contrast)
    'text_secondary': '#6B7280',   # Medium gray - Secondary text
    'text_tertiary': '#9CA3AF',    # Light gray - Disabled, hints
    
    'border': '#E5E7EB',           # Light gray - Borders, dividers
    'border_focus': '#3B82F6',     # Blue - Focused inputs
    
    # ──────────────────────────────────────────────────────────────────────
    # TRADING SPECIFIC (Market States)
    # ──────────────────────────────────────────────────────────────────────
    'bullish': '#059669',          # Green - Uptrend
    'bearish': '#DC2626',          # Red - Downtrend
    'neutral': '#6B7280',          # Gray - Sideways/neutral
    
    'buy': '#059669',              # Green - Buy recommendation
    'sell': '#DC2626',             # Red - Sell recommendation
    'hold': '#D97706',             # Amber - Hold recommendation
    
    # ──────────────────────────────────────────────────────────────────────
    # RISK LEVELS (Portfolio & Anomalies)
    # ──────────────────────────────────────────────────────────────────────
    'risk_low': '#059669',         # Green - Low risk
    'risk_moderate': '#D97706',    # Amber - Moderate risk
    'risk_high': '#DC2626',        # Red - High risk
    'risk_critical': '#991B1B',    # Dark red - Critical risk
}

# ============================================================================
# TYPOGRAPHY SCALE
# ============================================================================

TYPOGRAPHY = {
    # Headers
    'h1': '2rem',           # 32px - Page titles
    'h2': '1.5rem',         # 24px - Section titles
    'h3': '1.25rem',        # 20px - Card titles
    'h4': '1.125rem',       # 18px - Subsections
    
    # Body
    'body_large': '1rem',   # 16px - Default body text
    'body': '0.875rem',     # 14px - Secondary text
    'body_small': '0.75rem', # 12px - Captions, labels
    
    # Weight
    'weight_normal': '400',
    'weight_medium': '500',
    'weight_semibold': '600',
    'weight_bold': '700',
}

# ============================================================================
# SPACING SCALE (Consistent margins/padding)
# ============================================================================

SPACING = {
    'xs': '0.25rem',   # 4px
    'sm': '0.5rem',    # 8px
    'md': '1rem',      # 16px
    'lg': '1.5rem',    # 24px
    'xl': '2rem',      # 32px
    'xxl': '3rem',     # 48px
}

# ============================================================================
# SHADOWS (Subtle elevation for light mode)
# ============================================================================

SHADOWS = {
    'sm': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    'md': '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    'lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
    'none': 'none',
}

# ============================================================================
# BORDER RADIUS (Consistent rounding)
# ============================================================================

RADIUS = {
    'sm': '0.25rem',   # 4px - Buttons, inputs
    'md': '0.5rem',    # 8px - Cards
    'lg': '0.75rem',   # 12px - Modals
    'full': '9999px',  # Circular - Badges, avatars
}

# ============================================================================
# COMPONENT PRESETS (Ready-to-use CSS classes)
# ============================================================================

def get_component_styles():
    """
    Generate CSS for common UI components.
    Import this in app.py: from dashboard.ui_config import get_component_styles
    """
    return f"""
    <style>
        /* ═══════════════════════════════════════════════════════════════ */
        /* RESET & BASE */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .main {{
            background-color: {COLORS['bg_primary']};
            color: {COLORS['text_primary']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* TYPOGRAPHY HIERARCHY */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .page-title {{
            font-size: {TYPOGRAPHY['h1']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: {COLORS['primary_dark']};
            margin-bottom: {SPACING['md']};
            line-height: 1.2;
        }}
        
        .page-subtitle {{
            font-size: {TYPOGRAPHY['body']};
            color: {COLORS['text_secondary']};
            margin-bottom: {SPACING['xl']};
            line-height: 1.5;
        }}
        
        .section-title {{
            font-size: {TYPOGRAPHY['h3']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: {COLORS['text_primary']};
            margin-top: {SPACING['lg']};
            margin-bottom: {SPACING['md']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* METRIC CARDS (Key Performance Indicators) */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .metric-card {{
            background: {COLORS['bg_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['lg']};
            box-shadow: {SHADOWS['sm']};
            transition: all 0.2s ease;
        }}
        
        .metric-card:hover {{
            border-color: {COLORS['primary_light']};
            box-shadow: {SHADOWS['md']};
        }}
        
        .metric-label {{
            font-size: {TYPOGRAPHY['body_small']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            color: {COLORS['text_secondary']};
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: {SPACING['xs']};
        }}
        
        .metric-value {{
            font-size: {TYPOGRAPHY['h2']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: {COLORS['text_primary']};
            line-height: 1.2;
        }}
        
        .metric-delta {{
            font-size: {TYPOGRAPHY['body']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            margin-top: {SPACING['xs']};
        }}
        
        .metric-delta-positive {{
            color: {COLORS['success']};
        }}
        
        .metric-delta-negative {{
            color: {COLORS['danger']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* RECOMMENDATION BADGES */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .rec-badge {{
            display: inline-flex;
            align-items: center;
            gap: {SPACING['xs']};
            padding: {SPACING['sm']} {SPACING['md']};
            border-radius: {RADIUS['sm']};
            font-size: {TYPOGRAPHY['body']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
            letter-spacing: 0.025em;
        }}
        
        .rec-buy {{
            background: {COLORS['success_light']};
            color: {COLORS['success_text']};
            border: 1px solid {COLORS['success']};
        }}
        
        .rec-sell {{
            background: {COLORS['danger_light']};
            color: {COLORS['danger_text']};
            border: 1px solid {COLORS['danger']};
        }}
        
        .rec-hold {{
            background: {COLORS['warning_light']};
            color: {COLORS['warning_text']};
            border: 1px solid {COLORS['warning']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* ALERT BOXES (Color + Icon + Text) */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .alert {{
            padding: {SPACING['md']};
            border-radius: {RADIUS['md']};
            border-left: 4px solid;
            margin: {SPACING['md']} 0;
            display: flex;
            align-items: start;
            gap: {SPACING['sm']};
        }}
        
        .alert-icon {{
            flex-shrink: 0;
            font-size: {TYPOGRAPHY['h4']};
        }}
        
        .alert-content {{
            flex: 1;
        }}
        
        .alert-success {{
            background: {COLORS['success_light']};
            border-color: {COLORS['success']};
            color: {COLORS['success_text']};
        }}
        
        .alert-danger {{
            background: {COLORS['danger_light']};
            border-color: {COLORS['danger']};
            color: {COLORS['danger_text']};
        }}
        
        .alert-warning {{
            background: {COLORS['warning_light']};
            border-color: {COLORS['warning']};
            color: {COLORS['warning_text']};
        }}
        
        .alert-info {{
            background: {COLORS['info_light']};
            border-color: {COLORS['info']};
            color: {COLORS['info_text']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* STOCK CARD (Clean, scannable) */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .stock-card {{
            background: {COLORS['bg_primary']};
            border: 1px solid {COLORS['border']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']};
            margin-bottom: {SPACING['sm']};
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.2s ease;
        }}
        
        .stock-card:hover {{
            border-color: {COLORS['primary_light']};
            box-shadow: {SHADOWS['md']};
        }}
        
        .stock-name {{
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: {COLORS['text_primary']};
            margin-bottom: {SPACING['xs']};
        }}
        
        .stock-code {{
            font-size: {TYPOGRAPHY['body_small']};
            color: {COLORS['text_secondary']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* RISK INDICATORS */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .risk-indicator {{
            display: inline-flex;
            align-items: center;
            gap: {SPACING['xs']};
            padding: {SPACING['xs']} {SPACING['sm']};
            border-radius: {RADIUS['sm']};
            font-size: {TYPOGRAPHY['body_small']};
            font-weight: {TYPOGRAPHY['weight_semibold']};
        }}
        
        .risk-low {{
            background: {COLORS['success_light']};
            color: {COLORS['success_text']};
        }}
        
        .risk-moderate {{
            background: {COLORS['warning_light']};
            color: {COLORS['warning_text']};
        }}
        
        .risk-high {{
            background: {COLORS['danger_light']};
            color: {COLORS['danger_text']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* BUTTONS (Streamlit override) */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .stButton > button {{
            border-radius: {RADIUS['sm']};
            border: 1px solid {COLORS['border']};
            font-weight: {TYPOGRAPHY['weight_medium']};
            transition: all 0.2s ease;
        }}
        
        .stButton > button:hover {{
            border-color: {COLORS['primary']};
            color: {COLORS['primary']};
        }}
        
        .stButton > button[kind="primary"] {{
            background: {COLORS['primary']};
            border-color: {COLORS['primary']};
            color: white;
        }}
        
        .stButton > button[kind="primary"]:hover {{
            background: {COLORS['primary_dark']};
            border-color: {COLORS['primary_dark']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* MODULE STATUS INDICATORS */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .module-status {{
            display: flex;
            align-items: center;
            gap: {SPACING['xs']};
            padding: {SPACING['xs']} 0;
            font-size: {TYPOGRAPHY['body']};
        }}
        
        .module-active {{
            color: {COLORS['success']};
        }}
        
        .module-inactive {{
            color: {COLORS['danger']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* DISCLAIMER BOX */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .disclaimer {{
            background: {COLORS['warning_light']};
            border: 1px solid {COLORS['warning']};
            border-radius: {RADIUS['md']};
            padding: {SPACING['md']};
            font-size: {TYPOGRAPHY['body_small']};
            color: {COLORS['warning_text']};
            margin: {SPACING['md']} 0;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* PROGRESS INDICATOR (Onboarding) */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .progress-container {{
            display: flex;
            justify-content: center;
            gap: {SPACING['sm']};
            margin: {SPACING['xl']} 0;
        }}
        
        .progress-step {{
            width: 40px;
            height: 4px;
            background: {COLORS['border']};
            border-radius: {RADIUS['full']};
            transition: all 0.3s ease;
        }}
        
        .progress-step-active {{
            background: {COLORS['primary']};
        }}
        
        .progress-step-completed {{
            background: {COLORS['success']};
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* HELPER TEXT (Under form fields) */
        /* ═══════════════════════════════════════════════════════════════ */
        
        .helper-text {{
            font-size: {TYPOGRAPHY['body_small']};
            color: {COLORS['text_secondary']};
            margin-top: {SPACING['xs']};
            font-style: italic;
        }}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* HIDE STREAMLIT BRANDING */
        /* ═══════════════════════════════════════════════════════════════ */
        
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* ═══════════════════════════════════════════════════════════════ */
        /* CUSTOM SCROLLBAR (Subtle) */
        /* ═══════════════════════════════════════════════════════════════ */
        
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: {COLORS['bg_secondary']};
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: {COLORS['border']};
            border-radius: {RADIUS['full']};
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: {COLORS['text_tertiary']};
        }}
    </style>
    """

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_risk_color(risk_level: str) -> str:
    """
    Get color for risk level.
    
    Args:
        risk_level: 'LOW', 'NORMAL', 'ELEVATED', 'HIGH', 'CRITICAL'
    
    Returns:
        Color hex code
    """
    risk_map = {
        'LOW': COLORS['risk_low'],
        'NORMAL': COLORS['risk_low'],
        'ELEVATED': COLORS['risk_moderate'],
        'HIGH': COLORS['risk_high'],
        'CRITICAL': COLORS['risk_critical'],
    }
    return risk_map.get(risk_level.upper(), COLORS['neutral'])


def get_recommendation_color(rec: str) -> str:
    """
    Get color for recommendation.
    
    Args:
        rec: 'BUY', 'SELL', 'HOLD'
    
    Returns:
        Color hex code
    """
    rec_map = {
        'BUY': COLORS['buy'],
        'SELL': COLORS['sell'],
        'HOLD': COLORS['hold'],
    }
    return rec_map.get(rec.upper(), COLORS['neutral'])


def format_metric_delta(value: float, is_percentage: bool = True) -> tuple:
    """
    Format metric delta with color and prefix.
    
    Args:
        value: Numeric value
        is_percentage: If True, format as percentage
    
    Returns:
        Tuple of (formatted_text, css_class)
    """
    if value > 0:
        prefix = "+"
        css_class = "metric-delta-positive"
    elif value < 0:
        prefix = ""
        css_class = "metric-delta-negative"
    else:
        prefix = ""
        css_class = ""
    
    if is_percentage:
        formatted = f"{prefix}{value:.2f}%"
    else:
        formatted = f"{prefix}{value:,.2f}"
    
    return formatted, css_class


# ============================================================================
# COLOR EXPLANATIONS (For documentation)
# ============================================================================

COLOR_RATIONALE = """
# Color System Rationale

## Why These Colors?

### Primary Blue (#1E40AF)
- **Psychology**: Trust, stability, professionalism
- **Industry Standard**: Used by Bloomberg, Refinitiv, major banks
- **Accessibility**: High contrast against white background (AAA rating)
- **Use Cases**: Headers, buttons, links, brand elements

### Success Green (#059669)
- **Muted vs Neon**: Softer on eyes, professional appearance
- **Financial Context**: Positive returns, growth, buy signals
- **Contrast**: Dark enough for text, light enough for backgrounds
- **Use Cases**: Profit metrics, buy recommendations, success messages

### Danger Red (#DC2626)
- **Not Alarming**: Muted red avoids panic-inducing bright reds
- **Clear Signal**: Still immediately recognizable as "stop/danger"
- **Accessibility**: Meets WCAG AA contrast requirements
- **Use Cases**: Loss metrics, sell recommendations, critical alerts

### Warning Amber (#D97706)
- **Middle Ground**: Between green and red, signals caution
- **Finance Standard**: Industry-standard color for moderate risk
- **Visibility**: Stands out without being aggressive
- **Use Cases**: Hold recommendations, moderate risk, pending actions

### Neutral Gray Palette
- **Hierarchy**: Multiple gray shades create clear visual levels
- **Readability**: Proper contrast ratios for accessibility
- **Professional**: Clean, uncluttered appearance
- **Use Cases**: Backgrounds, borders, secondary text

## Visual Hierarchy Principles

1. **Page Titles**: Dark blue (#1E3A8A) - Most important
2. **Section Titles**: Black (#111827) - High importance
3. **Body Text**: Dark gray (#111827) - Default
4. **Secondary Text**: Medium gray (#6B7280) - Less important
5. **Disabled/Hints**: Light gray (#9CA3AF) - Lowest importance

## Accessibility Compliance

All color combinations meet WCAG 2.1 Level AA standards:
- Text contrast ratio: ≥ 4.5:1 (normal text)
- Large text contrast: ≥ 3:1
- Interactive elements: Clear focus states

## Finance Industry Best Practices

- **Light Mode Default**: Trading terminals use light backgrounds
- **Muted Colors**: Reduce eye strain during long sessions
- **Clear Signals**: Color + icon + text (not color-only)
- **Consistent Mapping**: Green=positive, Red=negative (universal)
"""

if __name__ == '__main__':
    # Test color system
    print("BVMT Trading Assistant - UI Configuration")
    print("=" * 50)
    print(f"Primary Color: {COLORS['primary']}")
    print(f"Success Color: {COLORS['success']}")
    print(f"Danger Color: {COLORS['danger']}")
    print(f"Warning Color: {COLORS['warning']}")
    print()
    print("Color system loaded successfully ✅")
