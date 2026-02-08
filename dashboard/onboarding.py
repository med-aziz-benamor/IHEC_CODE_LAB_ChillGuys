"""
Onboarding System - BVMT Trading Assistant
===========================================
Financial profile questionnaire with transparent scoring logic.

Design Philosophy:
- FINANCIAL PURPOSE: Every question directly impacts later decisions
- TRANSPARENCY: Users understand why each question matters
- SIMPLICITY: 5 questions maximum (3-5 minutes completion time)
- ACTIONABLE: Results directly influence recommendations

Scoring Logic:
- Each answer contributes to risk tolerance score (0-9)
- Profile determination:
  * Conservateur: 0-3 points
  * Modéré: 4-6 points
  * Agressif: 7-9 points
"""

import streamlit as st
from typing import Dict, Tuple

# ============================================================================
# QUESTION CONFIGURATION
# ============================================================================

QUESTIONS = {
    # ────────────────────────────────────────────────────────────────────────
    # Q1: Investment Horizon (Financial Purpose: Time = Risk Capacity)
    # ────────────────────────────────────────────────────────────────────────
    'horizon': {
        'number': 1,
        'title': "⏱️ Quel est votre horizon d'investissement ?",
        'helper': "Plus votre horizon est long, plus vous pouvez supporter la volatilité.",
        'options': {
            'Court terme (< 1 an)': {
                'score': 0,
                'risk': 'LOW',
                'explanation': 'Court terme = forte liquidité requise → portefeuille conservateur'
            },
            'Moyen terme (1-5 ans)': {
                'score': 1,
                'risk': 'MODERATE',
                'explanation': 'Moyen terme = équilibre entre croissance et stabilité'
            },
            'Long terme (> 5 ans)': {
                'score': 2,
                'risk': 'HIGH',
                'explanation': 'Long terme = capacité à traverser cycles de marché → plus de risque acceptable'
            },
        }
    },
    
    # ────────────────────────────────────────────────────────────────────────
    # Q2: Risk Tolerance (Financial Purpose: Emotional Capacity)
    # ────────────────────────────────────────────────────────────────────────
    'risk_tolerance': {
        'number': 2,
        'title': "🎯 Quelle perte maximale pouvez-vous accepter sur 1 an ?",
        'helper': "Soyez honnête : votre tolérance émotionnelle est aussi importante que vos objectifs.",
        'options': {
            'Aucune perte (0%)': {
                'score': 0,
                'risk': 'LOW',
                'explanation': 'Besoin de capital garanti → obligations/dépôts'
            },
            'Perte modérée (jusqu\'à 10%)': {
                'score': 1,
                'risk': 'MODERATE',
                'explanation': 'Tolérance moyenne → mix actions/obligations'
            },
            'Perte significative (10-20%)': {
                'score': 2,
                'risk': 'HIGH',
                'explanation': 'Haute tolérance → portefeuille orienté actions'
            },
        }
    },
    
    # ────────────────────────────────────────────────────────────────────────
    # Q3: Experience Level (Financial Purpose: Knowledge-based Risk)
    # ────────────────────────────────────────────────────────────────────────
    'experience': {
        'number': 3,
        'title': "📚 Quelle est votre expérience en Bourse tunisienne (BVMT) ?",
        'helper': "Les débutants ont besoin de stratégies plus simples et moins risquées.",
        'options': {
            'Débutant (aucune expérience)': {
                'score': 0,
                'risk': 'LOW',
                'explanation': 'Apprentissage requis → stratégies simples et éducatives'
            },
            'Intermédiaire (quelques transactions)': {
                'score': 1,
                'risk': 'MODERATE',
                'explanation': 'Connaissances de base acquises → diversification recommandée'
            },
            'Avancé (trading régulier)': {
                'score': 2,
                'risk': 'HIGH',
                'explanation': 'Expérience confirmée → stratégies sophistiquées accessibles'
            },
        }
    },
    
    # ────────────────────────────────────────────────────────────────────────
    # Q4: Capital to Invest (Financial Purpose: Position Sizing)
    # ────────────────────────────────────────────────────────────────────────
    'capital': {
        'number': 4,
        'title': "💰 Quel montant envisagez-vous d'investir (TND) ?",
        'helper': "Influence la diversification et les frais relatifs. Ne pas investir l'argent du loyer !",
        'options': {
            'Petit portefeuille (< 5,000 TND)': {
                'score': 0,
                'risk': 'LOW',
                'explanation': 'Capital limité → diversification réduite, ETF ou titres défensifs'
            },
            'Portefeuille moyen (5,000 - 20,000 TND)': {
                'score': 1,
                'risk': 'MODERATE',
                'explanation': 'Capital suffisant → bonne diversification possible (5-10 titres)'
            },
            'Grand portefeuille (> 20,000 TND)': {
                'score': 1,
                'risk': 'HIGH',
                'explanation': 'Capital important → forte diversification et stratégies avancées'
            },
        }
    },
    
    # ────────────────────────────────────────────────────────────────────────
    # Q5: Loss Reaction (Financial Purpose: Behavioral Finance)
    # ────────────────────────────────────────────────────────────────────────
    'loss_reaction': {
        'number': 5,
        'title': "😰 Si votre portefeuille perd 15% en 1 mois, que faites-vous ?",
        'helper': "Votre réaction aux pertes prédit votre succès en trading.",
        'options': {
            'Je vends immédiatement (panique)': {
                'score': 0,
                'risk': 'LOW',
                'explanation': 'Réaction émotionnelle forte → besoin de stabilité et éducation'
            },
            'J\'attends quelques jours puis je réévalue': {
                'score': 1,
                'risk': 'MODERATE',
                'explanation': 'Réaction mesurée → capable de gérer volatilité modérée'
            },
            'Je conserve et j\'analyse la situation': {
                'score': 2,
                'risk': 'HIGH',
                'explanation': 'Approche rationnelle → capacité à tenir positions long terme'
            },
        }
    },
}

# ============================================================================
# PROFILE DEFINITIONS
# ============================================================================

PROFILES = {
    'conservateur': {
        'emoji': '🛡️',
        'name': 'Conservateur',
        'score_range': (0, 3),
        'color': '#059669',  # Green (low risk)
        'description': "Vous privilégiez la préservation du capital et la stabilité.",
        'detailed_explanation': """
        ### 🛡️ Profil Conservateur
        
        **Caractéristiques :**
        - Priorité absolue : sécurité du capital
        - Tolérance au risque très faible
        - Horizon court à moyen terme
        - Préférence pour la liquidité
        
        **Stratégie recommandée :**
        - **60-70%** Obligations d'État tunisiennes
        - **20-30%** Actions défensives (banques, télécoms)
        - **10%** Liquidités
        
        **Objectif annuel :** 3-5% de rendement stable
        """,
        'allocation': {
            'Obligations': '60-70%',
            'Actions Défensives': '20-30%',
            'Liquidités': '10%',
        },
        'max_single_position': 10,  # % of portfolio
        'recommended_stocks': ['STB', 'BNA', 'ATB', 'ATTIJARI', 'TT'],  # Defensive
        'avoid_stocks': ['Small caps', 'High volatility stocks'],
    },
    
    'modere': {
        'emoji': '⚖️',
        'name': 'Modéré',
        'score_range': (4, 6),
        'color': '#D97706',  # Amber (moderate risk)
        'description': "Vous cherchez un équilibre entre croissance et sécurité.",
        'detailed_explanation': """
        ### ⚖️ Profil Modéré
        
        **Caractéristiques :**
        - Équilibre entre risque et rendement
        - Tolérance au risque moyenne
        - Horizon moyen à long terme
        - Acceptation de volatilité modérée
        
        **Stratégie recommandée :**
        - **40-50%** Actions diversifiées (blue chips + croissance)
        - **30-40%** Obligations corporate/gouvernementales
        - **10-20%** Liquidités/fonds monétaires
        
        **Objectif annuel :** 6-10% de rendement avec volatilité contrôlée
        """,
        'allocation': {
            'Actions Diversifiées': '40-50%',
            'Obligations': '30-40%',
            'Liquidités': '10-20%',
        },
        'max_single_position': 15,  # % of portfolio
        'recommended_stocks': ['All blue chips', 'Selected growth stocks'],
        'avoid_stocks': ['Extreme volatility stocks'],
    },
    
    'agressif': {
        'emoji': '🚀',
        'name': 'Agressif',
        'score_range': (7, 9),
        'color': '#DC2626',  # Red (high risk)
        'description': "Vous visez une forte croissance avec une tolérance élevée au risque.",
        'detailed_explanation': """
        ### 🚀 Profil Agressif
        
        **Caractéristiques :**
        - Objectif : maximiser les rendements
        - Haute tolérance au risque
        - Horizon long terme (> 5 ans)
        - Capacité à supporter forte volatilité
        
        **Stratégie recommandée :**
        - **70-85%** Actions (croissance + secteurs dynamiques)
        - **10-20%** Small/mid caps
        - **5-10%** Liquidités stratégiques
        
        **Objectif annuel :** 12-20%+ avec forte volatilité acceptée
        """,
        'allocation': {
            'Actions Croissance': '70-85%',
            'Small/Mid Caps': '10-20%',
            'Liquidités': '5-10%',
        },
        'max_single_position': 25,  # % of portfolio
        'recommended_stocks': ['High growth', 'Momentum stocks', 'Small caps'],
        'avoid_stocks': [],  # No restrictions
    },
}

# ============================================================================
# SCORING LOGIC
# ============================================================================

def calculate_profile_score(answers: Dict[str, str]) -> int:
    """
    Calculate risk tolerance score from questionnaire answers.
    
    Args:
        answers: Dict mapping question IDs to selected options
    
    Returns:
        Total score (0-8)
    
    Example:
        answers = {
            'horizon': 'Long terme (> 5 ans)',
            'risk_tolerance': 'Perte modérée (jusqu\'à 10%)',
            ...
        }
        score = calculate_profile_score(answers)  # Returns 4
    """
    total_score = 0
    
    for question_id, selected_option in answers.items():
        if question_id in QUESTIONS:
            question = QUESTIONS[question_id]
            if selected_option in question['options']:
                score = question['options'][selected_option]['score']
                total_score += score
    
    return total_score


def determine_profile(score: int) -> str:
    """
    Determine investment profile from score.
    
    Args:
        score: Risk tolerance score (0-8)
    
    Returns:
        Profile key ('conservateur', 'modere', 'agressif')
    """
    for profile_key, profile_data in PROFILES.items():
        min_score, max_score = profile_data['score_range']
        if min_score <= score <= max_score:
            return profile_key
    
    # Default fallback
    return 'modere'


def get_profile_display_name(profile: str) -> str:
    """
    Get display name with emoji for profile.
    
    Args:
        profile: Profile key
    
    Returns:
        Formatted name (e.g., "🛡️ Conservateur")
    """
    if profile in PROFILES:
        emoji = PROFILES[profile]['emoji']
        name = PROFILES[profile]['name']
        return f"{emoji} {name}"
    return profile


# ============================================================================
# ONBOARDING UI COMPONENTS
# ============================================================================

def render_progress_indicator(current_step: int, total_steps: int):
    """
    Render progress bar for onboarding.
    
    Args:
        current_step: Current question number (1-indexed)
        total_steps: Total number of questions
    """
    progress_html = '<div class="progress-container">'
    
    for step in range(1, total_steps + 1):
        if step < current_step:
            css_class = "progress-step progress-step-completed"
        elif step == current_step:
            css_class = "progress-step progress-step-active"
        else:
            css_class = "progress-step"
        progress_html += f'<div class="{css_class}"></div>'
    
    progress_html += '</div>'
    st.markdown(progress_html, unsafe_allow_html=True)


def render_question(question_id: str, question_data: Dict) -> str:
    """
    Render single question with radio buttons.
    
    Args:
        question_id: Question identifier
        question_data: Question configuration
    
    Returns:
        Selected option text
    """
    st.markdown(f"### {question_data['title']}")
    st.markdown(f'<p class="helper-text">{question_data["helper"]}</p>', unsafe_allow_html=True)
    
    options = list(question_data['options'].keys())
    selected = st.radio(
        label="Options",
        options=options,
        key=f"q_{question_id}",
        label_visibility="collapsed"
    )
    
    # Show explanation for selected option
    if selected:
        explanation = question_data['options'][selected]['explanation']
        st.info(f"💡 **Pourquoi ?** {explanation}")
    
    st.markdown("---")
    return selected


def render_profile_result(profile: str, score: int):
    """
    Display profile determination result with explanation.
    
    Args:
        profile: Profile key
        score: Total score achieved
    """
    profile_data = PROFILES[profile]
    
    # Header with emoji and profile name
    st.markdown(
        f"<div class='page-title' style='text-align: center; color: {profile_data['color']};'>"
        f"{profile_data['emoji']} Votre Profil : {profile_data['name'].upper()}</div>",
        unsafe_allow_html=True
    )
    
    # Short description
    st.markdown(
        f"<p style='text-align: center; font-size: 1.1rem; color: #6B7280;'>"
        f"{profile_data['description']}</p>",
        unsafe_allow_html=True
    )
    
    # Score display
    st.markdown(
        f"<p style='text-align: center; font-size: 0.9rem; color: #9CA3AF;'>"
        f"Score de risque : {score}/8</p>",
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Detailed explanation
    st.markdown(profile_data['detailed_explanation'])
    
    # Allocation guide
    with st.expander("📊 **Allocation d'actifs recommandée**", expanded=True):
        cols = st.columns(len(profile_data['allocation']))
        for i, (asset, percentage) in enumerate(profile_data['allocation'].items()):
            with cols[i]:
                st.metric(label=asset, value=percentage)
    
    # Why this profile?
    with st.expander("❓ **Pourquoi ce profil ?**"):
        st.markdown("""
        Votre profil a été déterminé en analysant :
        
        1. **Votre horizon d'investissement** → Capacité à supporter la volatilité
        2. **Votre tolérance aux pertes** → Seuil de confort psychologique
        3. **Votre expérience** → Niveau de sophistication acceptable
        4. **Votre capital** → Contraintes de diversification
        5. **Votre comportement** → Réaction émotionnelle face aux pertes
        
        Ce profil influencera :
        - ✅ Les recommandations d'achat/vente
        - ✅ La composition du portefeuille suggéré
        - ✅ Les seuils d'alerte personnalisés
        - ✅ Les indicateurs techniques affichés
        """)


def render_confirmation_screen():
    """
    Final confirmation before entering dashboard.
    """
    st.markdown(
        '<div class="page-title" style="text-align: center;">✅ Profil Enregistré</div>',
        unsafe_allow_html=True
    )
    
    st.success("""
    **🎯 Votre profil d'investisseur a été sauvegardé !**
    
    L'application va maintenant personnaliser :
    - Les recommandations selon votre tolérance au risque
    - Les alertes selon vos préférences
    - L'affichage des métriques pertinentes
    """)
    
    st.info("""
    **💡 Bon à savoir :**
    - Vous pouvez modifier votre profil à tout moment depuis le menu latéral
    - Les recommandations sont basées sur des modèles ML (ne constituent pas un conseil financier)
    - Diversifiez toujours vos investissements
    """)


# ============================================================================
# MAIN ONBOARDING FLOW
# ============================================================================

def run_onboarding():
    """
    Main onboarding flow with multi-step questionnaire.
    
    Returns:
        Tuple of (profile, score, answers) if completed, None otherwise
    """
    # Initialize session state
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    if 'onboarding_answers' not in st.session_state:
        st.session_state.onboarding_answers = {}
    
    step = st.session_state.onboarding_step
    total_questions = len(QUESTIONS)
    
    # ────────────────────────────────────────────────────────────────────────
    # Step 0: Welcome Screen
    # ────────────────────────────────────────────────────────────────────────
    if step == 0:
        st.markdown(
            '<div class="page-title" style="text-align: center;">👋 Bienvenue sur BVMT Trading Assistant</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<p class="page-subtitle" style="text-align: center;">'
            'Avant de commencer, aidez-nous à personnaliser votre expérience</p>',
            unsafe_allow_html=True
        )
        
        st.info("""
        **⏱️ Durée estimée : 2 minutes**
        
        Nous allons vous poser 5 questions rapides pour :
        - ✅ Déterminer votre profil d'investisseur
        - ✅ Adapter les recommandations à votre situation
        - ✅ Personnaliser les alertes et seuils de risque
        
        **🔒 Vos réponses restent locales (aucune connexion requise)**
        """)
        
        if st.button("📝 Commencer le questionnaire", type="primary", use_container_width=True):
            st.session_state.onboarding_step = 1
            st.rerun()
        
        return None
    
    # ────────────────────────────────────────────────────────────────────────
    # Steps 1-5: Questionnaire
    # ────────────────────────────────────────────────────────────────────────
    elif 1 <= step <= total_questions:
        # Progress indicator
        render_progress_indicator(step, total_questions)
        
        st.markdown(
            f'<p style="text-align: center; color: #9CA3AF; margin-bottom: 2rem;">'
            f'Question {step} sur {total_questions}</p>',
            unsafe_allow_html=True
        )
        
        # Get current question
        question_id = list(QUESTIONS.keys())[step - 1]
        question_data = QUESTIONS[question_id]
        
        # Render question
        selected_option = render_question(question_id, question_data)
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if step > 1:
                if st.button("⬅️ Précédent", use_container_width=True):
                    st.session_state.onboarding_step -= 1
                    st.rerun()
        
        with col3:
            button_label = "✅ Terminer" if step == total_questions else "Suivant ➡️"
            if st.button(button_label, type="primary", use_container_width=True):
                # Save answer
                st.session_state.onboarding_answers[question_id] = selected_option
                st.session_state.onboarding_step += 1
                st.rerun()
        
        return None
    
    # ────────────────────────────────────────────────────────────────────────
    # Step 6: Profile Result
    # ────────────────────────────────────────────────────────────────────────
    elif step == total_questions + 1:
        # Calculate profile
        answers = st.session_state.onboarding_answers
        score = calculate_profile_score(answers)
        profile = determine_profile(score)
        
        # Display result
        render_profile_result(profile, score)
        
        # Confirmation button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Accéder au tableau de bord", type="primary", use_container_width=True):
                # Save to session state
                st.session_state.profile = profile
                st.session_state.profile_score = score
                st.session_state.onboarding_completed = True
                st.session_state.onboarding_step = total_questions + 2
                st.rerun()
        
        # Back button
        if st.button("⬅️ Modifier mes réponses"):
            st.session_state.onboarding_step = 1
            st.rerun()
        
        return None
    
    # ────────────────────────────────────────────────────────────────────────
    # Step 7: Confirmation
    # ────────────────────────────────────────────────────────────────────────
    else:
        render_confirmation_screen()
        
        if st.button("✅ C'est compris, entrer dans l'app", type="primary", use_container_width=True):
            # Mark onboarding complete
            st.session_state.onboarding_completed = True
            st.rerun()
        
        return None


# ============================================================================
# UTILITY FUNCTIONS FOR APP INTEGRATION
# ============================================================================

def get_user_profile() -> dict:
    """
    Get current user profile from session state.
    
    Returns:
        Dict with profile information
    """
    if 'profile' not in st.session_state:
        return None
    
    profile_key = st.session_state.profile
    return {
        'key': profile_key,
        'name': PROFILES[profile_key]['name'],
        'emoji': PROFILES[profile_key]['emoji'],
        'score': st.session_state.get('profile_score', 0),
        'display_name': get_profile_display_name(profile_key),
        'data': PROFILES[profile_key],
    }


def reset_onboarding():
    """
    Reset onboarding state (for testing or profile change).
    """
    keys_to_remove = [
        'onboarding_step',
        'onboarding_answers',
        'onboarding_completed',
        'profile',
        'profile_score',
    ]
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]


def should_show_onboarding() -> bool:
    """
    Check if onboarding should be displayed.
    
    Returns:
        True if user hasn't completed onboarding
    """
    return not st.session_state.get('onboarding_completed', False)


# ============================================================================
# TESTING
# ============================================================================

if __name__ == '__main__':
    st.set_page_config(page_title="Onboarding Test", page_icon="📝", layout="wide")
    
    # Test onboarding flow
    if should_show_onboarding():
        run_onboarding()
    else:
        st.success(" Onboarding completed!")
        profile = get_user_profile()
        st.write(profile)
        
        if st.button("🔄 Reset Onboarding"):
            reset_onboarding()
            st.rerun()
