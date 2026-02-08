#!/usr/bin/env python3
"""
Internationalization (i18n) System
==================================
Multi-language support for BVMT Trading Assistant
Supports: French (FR), Arabic (AR), English (EN)

Usage:
    from dashboard.i18n import t, set_language, get_current_language, is_rtl
    
    # Set language
    set_language('fr')  # or 'ar' or 'en'
    
    # Get translation
    text = t('app.title')  # Returns "Assistant de Trading BVMT"
    
    # Check if current language is RTL
    if is_rtl():
        # Apply RTL layout
        pass
"""

# ============================================================================
# LANGUAGE DICTIONARIES
# ============================================================================

TRANSLATIONS = {
    # ========== FRENCH (DEFAULT) ==========
    'fr': {
        # App-level
        'app.title': 'Assistant de Trading BVMT',
        'app.subtitle': 'Système intelligent pour le marché tunisien',
        'app.team': 'Équipe: Rania • Chiraz • Malek • Aziz',
        'app.made_with': 'Made with ❤️ in Tunisia',
        
        # Navigation
        'nav.overview': 'Vue d\'Ensemble',
        'nav.analysis': 'Analyse Valeur',
        'nav.portfolio': 'Mon Portefeuille',
        'nav.alerts': 'Alertes',
        
        # Profile
        'profile.title': 'Profil d\'Investisseur',
        'profile.subtitle': 'Répondez à ces questions pour personnaliser vos recommandations.',
        'profile.conservative': 'Conservateur',
        'profile.moderate': 'Modéré',
        'profile.aggressive': 'Agressif',
        'profile.submit': 'Valider mon profil',
        'profile.determined': 'Profil défini',
        'profile.explanation_title': 'Pourquoi ce profil?',
        'profile.explanation_conservative': 'Vous privilégiez la sécurité et la préservation du capital. Votre portefeuille contiendra principalement des obligations et des actions stables.',
        'profile.explanation_moderate': 'Vous recherchez un équilibre entre croissance et sécurité. Votre portefeuille sera diversifié entre actions et obligations.',
        'profile.explanation_aggressive': 'Vous visez la croissance maximale et acceptez la volatilité. Votre portefeuille sera principalement composé d\'actions à fort potentiel.',
        
        # Questionnaire
        'q1.text': 'Quel est votre objectif d\'investissement principal?',
        'q1.opt1': 'Préserver mon capital',
        'q1.opt2': 'Équilibrer croissance et sécurité',
        'q1.opt3': 'Maximiser les gains',
        
        'q2.text': 'Comment réagiriez-vous à une perte de 10% en une semaine?',
        'q2.opt1': 'Je vendrais immédiatement',
        'q2.opt2': 'J\'attendrais avant de décider',
        'q2.opt3': 'J\'achèterais plus',
        
        'q3.text': 'Quelle est votre expérience en bourse?',
        'q3.opt1': 'Débutant',
        'q3.opt2': 'Intermédiaire',
        'q3.opt3': 'Avancé',
        
        'q4.text': 'Quel pourcentage de votre capital êtes-vous prêt à risquer?',
        
        # Modules
        'modules.status': 'Statut des Modules',
        'modules.data': 'Données',
        'modules.forecast': 'Prévision',
        'modules.sentiment': 'Sentiment',
        'modules.anomaly': 'Anomalies',
        'modules.decision': 'Décision',
        
        # Settings
        'settings.title': 'Paramètres',
        'settings.language': 'Langue',
        'settings.profile': 'Profil d\'investisseur',
        'settings.reset_portfolio': 'Réinitialiser Portefeuille',
        'settings.reset_success': 'Portefeuille réinitialisé!',
        
        # Overview Page
        'overview.title': 'Vue d\'Ensemble du Marché',
        'overview.subtitle': 'Tableau de bord intelligent pour le marché BVMT',
        'overview.market_trend': 'Tendance Marché',
        'overview.stocks_analyzed': 'Valeurs Analysées',
        'overview.active_alerts': 'Alertes Actives',
        'overview.portfolio_value': 'Valeur Portfolio',
        'overview.top_buys': 'Top Recommandations d\'Achat',
        'overview.top_sells': 'Alertes de Vente',
        'overview.suggested_portfolio': 'Portefeuille Suggéré pour Votre Profil',
        'overview.current_profile': 'Profil actuel',
        'overview.generate_portfolio': 'Générer un Portefeuille Diversifié',
        'overview.bullish': 'HAUSSIER',
        'overview.bearish': 'BAISSIER',
        'overview.neutral': 'NEUTRE',
        'overview.buy_signals': 'signaux achat',
        'overview.no_buys': 'Aucune recommandation d\'achat disponible',
        'overview.no_sells': 'Aucune alerte de vente active',
        
        # Analysis Page
        'analysis.title': 'Analyse Détaillée',
        'analysis.subtitle': 'Analyse approfondie d\'une valeur BVMT',
        'analysis.select_stock': 'Sélectionner une valeur',
        'analysis.select_prompt': 'Choisissez une valeur à analyser',
        'analysis.loading': 'Chargement des données...',
        'analysis.current_price': 'Prix Actuel',
        'analysis.variation': 'Variation',
        'analysis.volume': 'Volume',
        'analysis.recommendation': 'Recommandation',
        'analysis.confidence': 'Confiance',
        'analysis.price_history': 'Historique des Prix',
        'analysis.forecast': 'Prévision (5 jours)',
        'analysis.sentiment': 'Sentiment de Marché',
        'analysis.technical': 'Indicateurs Techniques',
        'analysis.anomaly': 'Détection d\'Anomalies',
        'analysis.explanation': 'Explication',
        'analysis.explain_button': 'Pourquoi cette recommandation?',
        'analysis.signal_breakdown': 'Contribution des Signaux',
        'analysis.add_to_portfolio': 'Ajouter au Portefeuille',
        
        # Technical Indicators
        'tech.rsi': 'RSI',
        'tech.rsi_info': 'Relative Strength Index - Mesure la force d\'une tendance (0-100)',
        'tech.rsi_oversold': 'Survd (< 30)',
        'tech.rsi_overbought': 'Surachat (> 70)',
        'tech.rsi_neutral': 'Neutre',
        'tech.macd': 'MACD',
        'tech.macd_info': 'Convergence-Divergence - Indicateur de momentum',
        'tech.bollinger': 'Bandes de Bollinger',
        'tech.bollinger_info': 'Mesure la volatilité et les niveaux de prix',
        
        # Portfolio Page
        'portfolio.title': 'Mon Portefeuille',
        'portfolio.subtitle': 'Gestion et suivi de vos positions',
        'portfolio.summary': 'Résumé',
        'portfolio.total_value': 'Valeur Totale',
        'portfolio.invested': 'Investi',
        'portfolio.return': 'Rendement',
        'portfolio.cash': 'Cash Disponible',
        'portfolio.allocation': 'Allocation du Portefeuille',
        'portfolio.holdings': 'Positions',
        'portfolio.no_holdings': 'Aucune position pour le moment. Visitez la page Analyse pour investir.',
        'portfolio.stock': 'Valeur',
        'portfolio.quantity': 'Quantité',
        'portfolio.avg_price': 'Prix Moyen',
        'portfolio.current_price': 'Prix Actuel',
        'portfolio.pl': 'P&L',
        'portfolio.actions': 'Actions',
        'portfolio.sell': 'Vendre',
        'portfolio.buy_more': 'Acheter +',
        'portfolio.performance': 'Performance',
        'portfolio.sharpe': 'Ratio de Sharpe',
        'portfolio.sharpe_info': 'Mesure le rendement ajusté au risque. > 1 est bon, > 2 est excellent.',
        'portfolio.max_drawdown': 'Max Drawdown',
        'portfolio.max_drawdown_info': 'Plus grande perte depuis un sommet. Indique le risque de baisse.',
        'portfolio.volatility': 'Volatilité',
        'portfolio.volatility_info': 'Écart-type des rendements. Plus c\'est élevé, plus c\'est risqué.',
        
        # Alerts Page
        'alerts.title': 'Surveillance & Alertes',
        'alerts.subtitle': 'Détection en temps réel des anomalies de marché',
        'alerts.show_all': 'Toutes',
        'alerts.show_high': 'Haute priorité',
        'alerts.show_medium': 'Moyenne priorité',
        'alerts.show_low': 'Basse priorité',
        'alerts.no_alerts': 'Aucune alerte active',
        'alerts.severity': 'Sévérité',
        'alerts.type': 'Type',
        'alerts.date': 'Date',
        'alerts.description': 'Description',
        'alerts.action': 'Action',
        'alerts.view_details': 'Voir détails',
        'alerts.dismiss': 'Ignorer',
        'alerts.acknowledged': 'Reconnu',
        'alerts.timeline': 'Timeline',
        
        # Recommendations
        'rec.buy': 'ACHETER',
        'rec.sell': 'VENDRE',
        'rec.hold': 'CONSERVER',
        
        # Common
        'common.loading': 'Chargement...',
        'common.error': 'Erreur',
        'common.success': 'Succès',
        'common.warning': 'Attention',
        'common.info': 'Information',
        'common.cancel': 'Annuler',
        'common.confirm': 'Confirmer',
        'common.close': 'Fermer',
        'common.save': 'Enregistrer',
        'common.na': 'N/A',
        'common.currency': 'TND',
        
        # Disclaimers
        'disclaimer.daily_data': '📊 Note: Analyse basée sur données journalières (non tick-by-tick)',
        'disclaimer.historical': '📅 Données historiques jusqu\'à 2025',
        'disclaimer.simulation': '⚠️ Portefeuille virtuel (simulation, non réel)',
        'disclaimer.not_advice': '⚖️ Ceci n\'est pas un conseil financier. Consultez un professionnel.',
    },
    
    # ========== ENGLISH ==========
    'en': {
        # App-level
        'app.title': 'BVMT Trading Assistant',
        'app.subtitle': 'Intelligent system for the Tunisian market',
        'app.team': 'Team: Rania • Chiraz • Malek • Aziz',
        'app.made_with': 'Made with ❤️ in Tunisia',
        
        # Navigation
        'nav.overview': 'Overview',
        'nav.analysis': 'Stock Analysis',
        'nav.portfolio': 'My Portfolio',
        'nav.alerts': 'Alerts',
        
        # Profile
        'profile.title': 'Investor Profile',
        'profile.subtitle': 'Answer these questions to personalize your recommendations.',
        'profile.conservative': 'Conservative',
        'profile.moderate': 'Moderate',
        'profile.aggressive': 'Aggressive',
        'profile.submit': 'Validate my profile',
        'profile.determined': 'Profile defined',
        'profile.explanation_title': 'Why this profile?',
        'profile.explanation_conservative': 'You prioritize security and capital preservation. Your portfolio will mainly contain bonds and stable stocks.',
        'profile.explanation_moderate': 'You seek a balance between growth and security. Your portfolio will be diversified between stocks and bonds.',
        'profile.explanation_aggressive': 'You aim for maximum growth and accept volatility. Your portfolio will mainly consist of high-potential stocks.',
        
        # Questionnaire
        'q1.text': 'What is your main investment objective?',
        'q1.opt1': 'Preserve my capital',
        'q1.opt2': 'Balance growth and security',
        'q1.opt3': 'Maximize gains',
        
        'q2.text': 'How would you react to a 10% loss in one week?',
        'q2.opt1': 'I would sell immediately',
        'q2.opt2': 'I would wait before deciding',
        'q2.opt3': 'I would buy more',
        
        'q3.text': 'What is your stock market experience?',
        'q3.opt1': 'Beginner',
        'q3.opt2': 'Intermediate',
        'q3.opt3': 'Advanced',
        
        'q4.text': 'What percentage of your capital are you willing to risk?',
        
        # Modules
        'modules.status': 'Module Status',
        'modules.data': 'Data',
        'modules.forecast': 'Forecast',
        'modules.sentiment': 'Sentiment',
        'modules.anomaly': 'Anomalies',
        'modules.decision': 'Decision',
        
        # Settings
        'settings.title': 'Settings',
        'settings.language': 'Language',
        'settings.profile': 'Investor profile',
        'settings.reset_portfolio': 'Reset Portfolio',
        'settings.reset_success': 'Portfolio reset!',
        
        # Overview Page
        'overview.title': 'Market Overview',
        'overview.subtitle': 'Intelligent dashboard for BVMT market',
        'overview.market_trend': 'Market Trend',
        'overview.stocks_analyzed': 'Stocks Analyzed',
        'overview.active_alerts': 'Active Alerts',
        'overview.portfolio_value': 'Portfolio Value',
        'overview.top_buys': 'Top Buy Recommendations',
        'overview.top_sells': 'Sell Alerts',
        'overview.suggested_portfolio': 'Suggested Portfolio for Your Profile',
        'overview.current_profile': 'Current profile',
        'overview.generate_portfolio': 'Generate Diversified Portfolio',
        'overview.bullish': 'BULLISH',
        'overview.bearish': 'BEARISH',
        'overview.neutral': 'NEUTRAL',
        'overview.buy_signals': 'buy signals',
        'overview.no_buys': 'No buy recommendations available',
        'overview.no_sells': 'No active sell alerts',
        
        # Analysis Page
        'analysis.title': 'Detailed Analysis',
        'analysis.subtitle': 'In-depth analysis of a BVMT stock',
        'analysis.select_stock': 'Select a stock',
        'analysis.select_prompt': 'Choose a stock to analyze',
        'analysis.loading': 'Loading data...',
        'analysis.current_price': 'Current Price',
        'analysis.variation': 'Change',
        'analysis.volume': 'Volume',
        'analysis.recommendation': 'Recommendation',
        'analysis.confidence': 'Confidence',
        'analysis.price_history': 'Price History',
        'analysis.forecast': 'Forecast (5 days)',
        'analysis.sentiment': 'Market Sentiment',
        'analysis.technical': 'Technical Indicators',
        'analysis.anomaly': 'Anomaly Detection',
        'analysis.explanation': 'Explanation',
        'analysis.explain_button': 'Why this recommendation?',
        'analysis.signal_breakdown': 'Signal Contribution',
        'analysis.add_to_portfolio': 'Add to Portfolio',
        
        # Technical Indicators
        'tech.rsi': 'RSI',
        'tech.rsi_info': 'Relative Strength Index - Measures trend strength (0-100)',
        'tech.rsi_oversold': 'Oversold (< 30)',
        'tech.rsi_overbought': 'Overbought (> 70)',
        'tech.rsi_neutral': 'Neutral',
        'tech.macd': 'MACD',
        'tech.macd_info': 'Moving Average Convergence Divergence - Momentum indicator',
        'tech.bollinger': 'Bollinger Bands',
        'tech.bollinger_info': 'Measures volatility and price levels',
        
        # Portfolio Page
        'portfolio.title': 'My Portfolio',
        'portfolio.subtitle': 'Manage and track your positions',
        'portfolio.summary': 'Summary',
        'portfolio.total_value': 'Total Value',
        'portfolio.invested': 'Invested',
        'portfolio.return': 'Return',
        'portfolio.cash': 'Available Cash',
        'portfolio.allocation': 'Portfolio Allocation',
        'portfolio.holdings': 'Holdings',
        'portfolio.no_holdings': 'No positions yet. Visit the Analysis page to invest.',
        'portfolio.stock': 'Stock',
        'portfolio.quantity': 'Quantity',
        'portfolio.avg_price': 'Avg Price',
        'portfolio.current_price': 'Current Price',
        'portfolio.pl': 'P&L',
        'portfolio.actions': 'Actions',
        'portfolio.sell': 'Sell',
        'portfolio.buy_more': 'Buy More',
        'portfolio.performance': 'Performance',
        'portfolio.sharpe': 'Sharpe Ratio',
        'portfolio.sharpe_info': 'Measures risk-adjusted return. > 1 is good, > 2 is excellent.',
        'portfolio.max_drawdown': 'Max Drawdown',
        'portfolio.max_drawdown_info': 'Largest loss from peak. Indicates downside risk.',
        'portfolio.volatility': 'Volatility',
        'portfolio.volatility_info': 'Standard deviation of returns. Higher means riskier.',
        
        # Alerts Page
        'alerts.title': 'Monitoring & Alerts',
        'alerts.subtitle': 'Real-time detection of market anomalies',
        'alerts.show_all': 'All',
        'alerts.show_high': 'High priority',
        'alerts.show_medium': 'Medium priority',
        'alerts.show_low': 'Low priority',
        'alerts.no_alerts': 'No active alerts',
        'alerts.severity': 'Severity',
        'alerts.type': 'Type',
        'alerts.date': 'Date',
        'alerts.description': 'Description',
        'alerts.action': 'Action',
        'alerts.view_details': 'View details',
        'alerts.dismiss': 'Dismiss',
        'alerts.acknowledged': 'Acknowledged',
        'alerts.timeline': 'Timeline',
        
        # Recommendations
        'rec.buy': 'BUY',
        'rec.sell': 'SELL',
        'rec.hold': 'HOLD',
        
        # Common
        'common.loading': 'Loading...',
        'common.error': 'Error',
        'common.success': 'Success',
        'common.warning': 'Warning',
        'common.info': 'Information',
        'common.cancel': 'Cancel',
        'common.confirm': 'Confirm',
        'common.close': 'Close',
        'common.save': 'Save',
        'common.na': 'N/A',
        'common.currency': 'TND',
        
        # Disclaimers
        'disclaimer.daily_data': '📊 Note: Analysis based on daily data (not tick-by-tick)',
        'disclaimer.historical': '📅 Historical data up to 2025',
        'disclaimer.simulation': '⚠️ Virtual portfolio (simulation, not real)',
        'disclaimer.not_advice': '⚖️ This is not financial advice. Consult a professional.',
    },
    
    # ========== ARABIC ==========
    'ar': {
        # App-level
        'app.title': 'مساعد التداول BVMT',
        'app.subtitle': 'نظام ذكي للسوق التونسي',
        'app.team': 'الفريق: رانيا • شيراز • مالك • عزيز',
        'app.made_with': 'صُنع بـ ❤️ في تونس',
        
        # Navigation
        'nav.overview': 'نظرة عامة',
        'nav.analysis': 'تحليل الأسهم',
        'nav.portfolio': 'محفظتي',
        'nav.alerts': 'التنبيهات',
        
        # Profile
        'profile.title': 'ملف المستثمر',
        'profile.subtitle': 'أجب على هذه الأسئلة لتخصيص توصياتك.',
        'profile.conservative': 'محافظ',
        'profile.moderate': 'معتدل',
        'profile.aggressive': 'جريء',
        'profile.submit': 'تأكيد ملفي',
        'profile.determined': 'تم تحديد الملف',
        'profile.explanation_title': 'لماذا هذا الملف؟',
        'profile.explanation_conservative': 'أنت تعطي الأولوية للأمان والحفاظ على رأس المال. ستحتوي محفظتك بشكل أساسي على سندات وأسهم مستقرة.',
        'profile.explanation_moderate': 'أنت تبحث عن توازن بين النمو والأمان. ستكون محفظتك متنوعة بين الأسهم والسندات.',
        'profile.explanation_aggressive': 'أنت تهدف إلى النمو الأقصى وتقبل التقلبات. ستتكون محفظتك بشكل أساسي من أسهم ذات إمكانات عالية.',
        
        # Questionnaire
        'q1.text': 'ما هو هدفك الاستثماري الرئيسي؟',
        'q1.opt1': 'الحفاظ على رأس مالي',
        'q1.opt2': 'الموازنة بين النمو والأمان',
        'q1.opt3': 'تعظيم الأرباح',
        
        'q2.text': 'كيف ستتفاعل مع خسارة 10٪ في أسبوع؟',
        'q2.opt1': 'سأبيع فوراً',
        'q2.opt2': 'سأنتظر قبل اتخاذ القرار',
        'q2.opt3': 'سأشتري المزيد',
        
        'q3.text': 'ما هي خبرتك في سوق الأسهم؟',
        'q3.opt1': 'مبتدئ',
        'q3.opt2': 'متوسط',
        'q3.opt3': 'متقدم',
        
        'q4.text': 'ما النسبة المئوية من رأس مالك التي أنت على استعداد للمخاطرة بها؟',
        
        # Modules
        'modules.status': 'حالة الوحدات',
        'modules.data': 'البيانات',
        'modules.forecast': 'التنبؤ',
        'modules.sentiment': 'المشاعر',
        'modules.anomaly': 'الشذوذ',
        'modules.decision': 'القرار',
        
        # Settings
        'settings.title': 'الإعدادات',
        'settings.language': 'اللغة',
        'settings.profile': 'ملف المستثمر',
        'settings.reset_portfolio': 'إعادة تعيين المحفظة',
        'settings.reset_success': 'تم إعادة تعيين المحفظة!',
        
        # Overview Page
        'overview.title': 'نظرة عامة على السوق',
        'overview.subtitle': 'لوحة تحكم ذكية لسوق BVMT',
        'overview.market_trend': 'اتجاه السوق',
        'overview.stocks_analyzed': 'الأسهم المحللة',
        'overview.active_alerts': 'التنبيهات النشطة',
        'overview.portfolio_value': 'قيمة المحفظة',
        'overview.top_buys': 'أفضل توصيات الشراء',
        'overview.top_sells': 'تنبيهات البيع',
        'overview.suggested_portfolio': 'المحفظة المقترحة لملفك',
        'overview.current_profile': 'الملف الحالي',
        'overview.generate_portfolio': 'إنشاء محفظة متنوعة',
        'overview.bullish': 'صاعد',
        'overview.bearish': 'هابط',
        'overview.neutral': 'محايد',
        'overview.buy_signals': 'إشارات الشراء',
        'overview.no_buys': 'لا توجد توصيات شراء متاحة',
        'overview.no_sells': 'لا توجد تنبيهات بيع نشطة',
        
        # Analysis Page
        'analysis.title': 'تحليل مفصل',
        'analysis.subtitle': 'تحليل متعمق لسهم BVMT',
        'analysis.select_stock': 'اختر سهماً',
        'analysis.select_prompt': 'اختر سهماً للتحليل',
        'analysis.loading': 'جارٍ تحميل البيانات...',
        'analysis.current_price': 'السعر الحالي',
        'analysis.variation': 'التغيير',
        'analysis.volume': 'الحجم',
        'analysis.recommendation': 'التوصية',
        'analysis.confidence': 'الثقة',
        'analysis.price_history': 'تاريخ الأسعار',
        'analysis.forecast': 'التنبؤ (5 أيام)',
        'analysis.sentiment': 'معنويات السوق',
        'analysis.technical': 'المؤشرات الفنية',
        'analysis.anomaly': 'كشف الشذوذ',
        'analysis.explanation': 'التفسير',
        'analysis.explain_button': 'لماذا هذه التوصية؟',
        'analysis.signal_breakdown': 'مساهمة الإشارات',
        'analysis.add_to_portfolio': 'إضافة إلى المحفظة',
        
        # Technical Indicators
        'tech.rsi': 'مؤشر القوة النسبية',
        'tech.rsi_info': 'يقيس قوة الاتجاه (0-100)',
        'tech.rsi_oversold': 'ذروة البيع (< 30)',
        'tech.rsi_overbought': 'ذروة الشراء (> 70)',
        'tech.rsi_neutral': 'محايد',
        'tech.macd': 'MACD',
        'tech.macd_info': 'مؤشر الزخم',
        'tech.bollinger': 'نطاقات بولينجر',
        'tech.bollinger_info': 'يقيس التقلب ومستويات الأسعار',
        
        # Portfolio Page
        'portfolio.title': 'محفظتي',
        'portfolio.subtitle': 'إدارة وتتبع مراكزك',
        'portfolio.summary': 'ملخص',
        'portfolio.total_value': 'القيمة الإجمالية',
        'portfolio.invested': 'المستثمر',
        'portfolio.return': 'العائد',
        'portfolio.cash': 'النقد المتاح',
        'portfolio.allocation': 'توزيع المحفظة',
        'portfolio.holdings': 'المراكز',
        'portfolio.no_holdings': 'لا توجد مراكز حتى الآن. قم بزيارة صفحة التحليل للاستثمار.',
        'portfolio.stock': 'السهم',
        'portfolio.quantity': 'الكمية',
        'portfolio.avg_price': 'متوسط السعر',
        'portfolio.current_price': 'السعر الحالي',
        'portfolio.pl': 'الربح/الخسارة',
        'portfolio.actions': 'الإجراءات',
        'portfolio.sell': 'بيع',
        'portfolio.buy_more': 'شراء المزيد',
        'portfolio.performance': 'الأداء',
        'portfolio.sharpe': 'نسبة شارب',
        'portfolio.sharpe_info': 'يقيس العائد المعدل حسب المخاطر. > 1 جيد، > 2 ممتاز.',
        'portfolio.max_drawdown': 'أقصى انخفاض',
        'portfolio.max_drawdown_info': 'أكبر خسارة من القمة. يشير إلى مخاطر الهبوط.',
        'portfolio.volatility': 'التقلب',
        'portfolio.volatility_info': 'الانحراف المعياري للعوائد. كلما زاد، زادت المخاطر.',
        
        # Alerts Page
        'alerts.title': 'المراقبة والتنبيهات',
        'alerts.subtitle': 'كشف في الوقت الفعلي لشذوذ السوق',
        'alerts.show_all': 'الكل',
        'alerts.show_high': 'أولوية عالية',
        'alerts.show_medium': 'أولوية متوسطة',
        'alerts.show_low': 'أولوية منخفضة',
        'alerts.no_alerts': 'لا توجد تنبيهات نشطة',
        'alerts.severity': 'الخطورة',
        'alerts.type': 'النوع',
        'alerts.date': 'التاريخ',
        'alerts.description': 'الوصف',
        'alerts.action': 'الإجراء',
        'alerts.view_details': 'عرض التفاصيل',
        'alerts.dismiss': 'تجاهل',
        'alerts.acknowledged': 'تم الإقرار',
        'alerts.timeline': 'الجدول الزمني',
        
        # Recommendations
        'rec.buy': 'شراء',
        'rec.sell': 'بيع',
        'rec.hold': 'احتفظ',
        
        # Common
        'common.loading': 'جارٍ التحميل...',
        'common.error': 'خطأ',
        'common.success': 'نجاح',
        'common.warning': 'تحذير',
        'common.info': 'معلومات',
        'common.cancel': 'إلغاء',
        'common.confirm': 'تأكيد',
        'common.close': 'إغلاق',
        'common.save': 'حفظ',
        'common.na': 'غير متوفر',
        'common.currency': 'دينار',
        
        # Disclaimers
        'disclaimer.daily_data': '📊 ملاحظة: التحليل بناءً على البيانات اليومية (وليس اللحظية)',
        'disclaimer.historical': '📅 بيانات تاريخية حتى 2025',
        'disclaimer.simulation': '⚠️ محفظة افتراضية (محاكاة، ليست حقيقية)',
        'disclaimer.not_advice': '⚖️ هذه ليست نصيحة مالية. استشر متخصصاً.',
    }
}

# ============================================================================
# CURRENT LANGUAGE STATE
# ============================================================================

_current_language = 'fr'  # Default language

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def set_language(lang_code: str) -> None:
    """
    Set the current language for the application.
    
    Args:
        lang_code: Language code ('fr', 'ar', 'en')
    """
    global _current_language
    if lang_code in TRANSLATIONS:
        _current_language = lang_code
    else:
        raise ValueError(f"Unsupported language: {lang_code}. Available: {list(TRANSLATIONS.keys())}")


def get_current_language() -> str:
    """Get the current language code."""
    return _current_language


def t(key: str, **kwargs) -> str:
    """
    Translate a key to the current language.
    
    Args:
        key: Translation key (e.g., 'app.title')
        **kwargs: Optional parameters for string formatting
    
    Returns:
        Translated string or key if not found (with fallback to French)
    
    Example:
        >>> set_language('en')
        >>> t('app.title')
        'BVMT Trading Assistant'
        >>> t('welcome', name='Ahmed')
        'Welcome Ahmed!' (if key exists with {name} placeholder)
    """
    lang = get_current_language()
    translations = TRANSLATIONS.get(lang, TRANSLATIONS['fr'])
    
    # Get translation with fallback to French
    text = translations.get(key)
    if text is None and lang != 'fr':
        text = TRANSLATIONS['fr'].get(key)
    if text is None:
        return f"[{key}]"  # Return key in brackets if not found
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # Ignore missing format keys
    
    return text


def is_rtl() -> bool:
    """Check if current language is right-to-left (RTL)."""
    return get_current_language() == 'ar'


def get_language_name(lang_code: str) -> str:
    """Get the display name of a language."""
    names = {
        'fr': 'Français 🇫🇷',
        'en': 'English 🇬🇧',
        'ar': 'العربية 🇹🇳'
    }
    return names.get(lang_code, lang_code)


def get_available_languages() -> list:
    """Get list of available language codes."""
    return list(TRANSLATIONS.keys())


def get_rtl_css() -> str:
    """
    Get CSS for RTL layout when Arabic is selected.
    
    Returns:
        CSS string for RTL or empty string
    """
    if not is_rtl():
        return ""
    
    return """
    <style>
        /* RTL Support for Arabic */
        .main .block-container {
            direction: rtl;
            text-align: right;
        }
        
        .stMarkdown, .stText {
            direction: rtl;
            text-align: right;
        }
        
        /* Reverse column order for RTL */
        .row-widget.stHorizontal {
            flex-direction: row-reverse;
        }
        
        /* Sidebar RTL */
        .css-1d391kg, [data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }
        
        /* Button alignment */
        .stButton > button {
            direction: rtl;
        }
        
        /* Metric cards RTL */
        .metric-card {
            direction: rtl;
            text-align: right;
            border-right: 4px solid #1f77b4;
            border-left: none;
        }
        
        /* Stock cards RTL */
        .stock-card {
            flex-direction: row-reverse;
        }
        
        /* Alert boxes RTL */
        .alert-critical, .alert-warning, .alert-info, .alert-success {
            border-right: 4px solid;
            border-left: none;
            text-align: right;
        }
    </style>
    """


# ============================================================================
# LANGUAGE SELECTOR WIDGET
# ============================================================================

def render_language_selector(session_state_key='language'):
    """
    Render a language selector widget for Streamlit.
    
    Args:
        session_state_key: Key to store language in st.session_state
    
    Returns:
        Selected language code
    
    Usage in Streamlit:
        ```python
        import streamlit as st
        from dashboard.i18n import render_language_selector, t, get_rtl_css
        
        # Render selector
        lang = render_language_selector('app_language')
        
        # Apply RTL if Arabic
        st.markdown(get_rtl_css(), unsafe_allow_html=True)
        
        # Use translations
        st.title(t('app.title'))
        ```
    """
    import streamlit as st
    
    # Initialize session state if needed
    if session_state_key not in st.session_state:
        st.session_state[session_state_key] = 'fr'
    
    # Language options
    languages = {
        'fr': 'Français 🇫🇷',
        'en': 'English 🇬🇧',
        'ar': 'العربية 🇹🇳'
    }
    
    # Render selector
    selected = st.selectbox(
        t('settings.language'),
        options=list(languages.keys()),
        format_func=lambda x: languages[x],
        key=session_state_key,
        index=list(languages.keys()).index(st.session_state[session_state_key])
    )
    
    # Update global language
    if selected != get_current_language():
        set_language(selected)
        st.session_state[session_state_key] = selected
    
    return selected


# ============================================================================
# PROFILE EMOJI HELPERS
# ============================================================================

def get_profile_emoji(profile: str) -> str:
    """Get emoji for investor profile."""
    emojis = {
        'conservative': '🛡️',
        'moderate': '⚖️',
        'aggressive': '🚀'
    }
    return emojis.get(profile, '⚖️')


def get_profile_name(profile: str) -> str:
    """Get translated profile name with emoji."""
    emoji = get_profile_emoji(profile)
    name = t(f'profile.{profile}')
    return f"{emoji} {name}"


# ============================================================================
# MODULE END
# ============================================================================

if __name__ == '__main__':
    # Test translations
    print("=== i18n System Test ===\n")
    
    for lang in ['fr', 'en', 'ar']:
        set_language(lang)
        print(f"Language: {get_language_name(lang)} (RTL: {is_rtl()})")
        print(f"  Title: {t('app.title')}")
        print(f"  Profile: {get_profile_name('moderate')}")
        print(f"  Buy: {t('rec.buy')}")
        print()
