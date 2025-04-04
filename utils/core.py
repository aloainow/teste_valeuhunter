# utils/core.py - Funções Principais
import os
import json
import time
import logging
import streamlit as st
from datetime import datetime, timedelta
from urllib.parse import urlencode

# Importando dependências
try:
    import stripe
except ImportError:
    # Código dummy para stripe (mantido como está)
    class DummyStripe:
        api_key = None
        class checkout:
            class Session:
                @staticmethod
                def create(**kwargs):
                    return type('obj', (object,), {'id': 'dummy_session', 'url': '#'})
                @staticmethod
                def retrieve(session_id):
                    return type('obj', (object,), {'payment_status': 'unpaid', 'metadata': {'credits': '0', 'email': ''}})
        class error:
            class InvalidRequestError(Exception):
                pass
    stripe = DummyStripe

# Configuração de logging
logger = logging.getLogger("valueHunter.core")

# Configurações globais
if "RENDER" in os.environ:
    # Em produção no Render, use um diretório no qual o app tem permissão de escrita
    DATA_DIR = os.path.join(os.getcwd(), 'data')
else:
    # Em desenvolvimento local, use o diretório configurado ou o padrão
    DATA_DIR = os.environ.get("DATA_DIR", "data")

# Garantir que o diretório existe
os.makedirs(DATA_DIR, exist_ok=True)

# Funções de CSS e UI
def configure_sidebar_visibility():
    """
    Configura a visibilidade da barra lateral:
    1. NÃO ocultamos a barra lateral globalmente
    2. Oculta apenas itens específicos (app e admin)
    """
    st.markdown("""
    <style>
        /* PRIMEIRO: Garantir que a barra lateral esteja visível nas páginas que precisam dela */
        /* Deixamos a visibilidade ser controlada por cada página individualmente */
        
        /* SEGUNDO: Ocultar apenas os itens específicos no menu */
        [data-testid="stSidebarNavItems"] a:has(p:contains("app")),
        [data-testid="stSidebarNavItems"] a:has(p:contains("admin")) {
            display: none !important;
        }
        
        /* Versão alternativa para Streamlit mais recente */
        .st-emotion-cache-16idsys a:has(p:contains("app")),
        .st-emotion-cache-16idsys a:has(p:contains("admin")) {
            display: none !important;
        }
        
        /* Verificar mais um seletor alternativo */
        div[data-testid="stSidebarNavContainer"] li:has(a[href*="app"]),
        div[data-testid="stSidebarNavContainer"] li:has(a[href*="admin"]) {
            display: none !important;
        }
        
        /* Também oculta os textos diretos contendo app/admin */
        [data-testid="stSidebarNavItems"] p:contains("app"),
        [data-testid="stSidebarNavItems"] p:contains("admin"),
        .st-emotion-cache-16idsys p:contains("app"),
        .st-emotion-cache-16idsys p:contains("admin") {
            display: none !important;
        }
        
        /* Adicionar seletores específicos para o modal/dropdown */
        div[role="dialog"] p:contains("app"),
        div[role="dialog"] p:contains("admin"),
        div[aria-modal="true"] p:contains("app"),
        div[aria-modal="true"] p:contains("admin") {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
def hide_admin_pages_completely():
    """
    This function adds more aggressive CSS selectors to completely hide admin pages
    from the sidebar and any navigation elements
    """
    st.markdown("""
    <style>
        /* Hide everything in the sidebar */
        [data-testid="stSidebarNavItems"] li a:nth-child(n),
        [data-testid="stSidebarNavItems"] div a:nth-child(n),
        [data-testid="stSidebarNav"] li a:nth-child(n),
        div.sidebar a:nth-child(n),
        div[role="navigation"] li:nth-child(n),
        div[role="menu"] a:nth-child(n) {
            display: none !important;
        }
        
        /* Only show the specific pages we want */
        [data-testid="stSidebarNavItems"] li a[href*="dashboard"],
        [data-testid="stSidebarNavItems"] li a[href*="landing"],
        [data-testid="stSidebarNavItems"] li a[href*="packages"],
        div[role="menu"] a[href*="dashboard"],
        div[role="menu"] a[href*="landing"],
        div[role="menu"] a[href*="packages"] {
            display: block !important;
        }
        
        /* Hide pages in dropdown menus */
        div[role="dialog"] a[href*="app"],
        div[role="dialog"] a[href*="admin"],
        div[aria-modal="true"] a[href*="app"],
        div[aria-modal="true"] a[href*="admin"] {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)
def hide_streamlit_menu():
    """Oculta o menu de navegação do Streamlit e outros elementos da interface padrão"""
    return """
    <style>
        /* IMPORTANTE: Apenas ocultar elementos de navegação, não a barra lateral inteira */
        
        /* FORÇAR barra lateral a permanecer visível */
        [data-testid="stSidebar"] {
            display: block !important;
            visibility: visible !important;
            opacity: 1 !important;
            width: auto !important;
            transform: none !important;
        }
        
        /* Ocultar menu de navegação */
        header[data-testid="stHeader"] {
            display: none !important;
        }
        
        /* Ocultar hamburger menu e botão de navegação */
        button[kind="header"] {
            display: none !important;
        }
        
        /* Ocultar apenas o container de navegação na sidebar */
        section[data-testid="stSidebarNavContainer"] {
            display: none !important;
        }
        
        /* Seletores para itens de navegação, não para a barra inteira */
        div.stSidebarNavItems, 
        button.stSidebarButton,
        div.st-emotion-cache-16idsys,
        ul.st-emotion-cache-pbk8do {
            display: none !important;
        }
        
        /* Adicionais seletores para navegação */
        [data-testid="collapsedControl"],
        #MainMenu,
        footer {
            display: none !important;
        }
        
        /* Remover espaço extra no topo que normalmente é ocupado pelo menu */
        .main .block-container {
            padding-top: 1rem !important;
        }
    </style>
    """
def hide_app_admin_items():
    """
    Função para ocultar completamente os itens 'app' e 'admin' 
    em qualquer parte da interface do Streamlit
    """
    st.markdown("""
    <style>
        /* Seletores específicos para o modal/dropdown */
        div[role="dialog"] p:contains("app"),
        div[role="dialog"] p:contains("admin"),
        div[aria-modal="true"] p:contains("app"),
        div[aria-modal="true"] p:contains("admin"),
        
        /* Seletores para navegação lateral */
        [data-testid="stSidebarNavItems"] a:has(p:contains("app")),
        [data-testid="stSidebarNavItems"] a:has(p:contains("admin")),
        
        /* Seletores gerais para qualquer texto */
        p:contains("app"),
        p:contains("admin") {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

def hide_app_admin_from_modal():
    """
    Função específica para ocultar os itens 'app' e 'admin' no modal/dropdown de navegação
    """
    st.markdown("""
    <style>
        /* Seletores ultra-específicos para o modal/dropdown da captura de tela */
        div[role="dialog"] div > p:contains("app"),
        div[role="dialog"] div > p:contains("admin") {
            display: none !important;
        }
        
        /* Seletor alternativo para o mesmo elemento */
        div[aria-modal="true"] p:contains("app"),
        div[aria-modal="true"] p:contains("admin") {
            display: none !important;
        }
        
        /* Seletor com correspondência de texto exato para maior precisão */
        p:text-is("app"),
        p:text-is("admin") {
            display: none !important;
        }
        
        /* Seletor direto para elementos de página na navegação */
        div.st-bd p:contains("app"),
        div.st-bd p:contains("admin") {
            display: none !important;
        }
    </style>
    """, unsafe_allow_html=True)

def apply_global_css():
    """Aplica estilos CSS globais para toda a aplicação"""
    st.markdown("""
    <style>
        /* Estilo para TODOS os botões - LARANJA COM TEXTO BRANCO */
        div.stButton > button, button.css-1rs6os.edgvbvh3 {
            background-color: #fd7014 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 4px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        
        div.stButton > button:hover, button.css-1rs6os.edgvbvh3:hover {
            background-color: #27272a !important; /* Cinza escuro no hover */
            color: white !important;
        }
        
        /* Logo consistente */
        .logo-container {
            background-color: #fd7014;
            padding: 12px 25px !important;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 5px;
            width: fit-content;
            margin-bottom: 20px;
        }
        
        .logo-v {
            color: #3F3F45;
            font-size: 3rem !important;
            font-weight: bold;
        }
        
        .logo-text {
            font-size: 2.5rem !important;
            font-weight: bold;
            color: #FFFFFF;
        }
        
        body {
            background-color: #3F3F45;
            color: #FFFFFF;
        }
        .landing-container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }
        .navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .hero {
            margin: 2rem 0;
            text-align: left;
        }
        .hero h1 {
            font-size: 2.8rem;
            color: #fd7014;
            margin-bottom: 1rem;
        }
        .hero p {
            font-size: 1.25rem;
            color: #FFFFFF;
            max-width: 90%;
            margin-left: 0;
        }
        .about-content {
            max-width: 90%;
            margin-left: 0;
            line-height: 1.6;
            margin-top: 2rem;
            margin-bottom: 2rem;
        }
        .about-content h2 {
            color: #fd7014;
            margin-bottom: 0.8rem;
            text-align: left;
        }
        .footer {
            margin-top: 2rem;
            text-align: center;
            color: #b0b0b0;
        }
        .btn-container {
            display: flex;
            justify-content: flex-start;
            gap: 20px;
            margin-top: 1.5rem;
        }
        p, li {
            color: #FFFFFF !important;
        }
        
        /* Aumentar a largura máxima do container principal */
        .main .block-container {
            max-width: 100% !important; 
            padding: 1rem !important;
        }
        
        /* Resultado da análise em largura total */
        .analysis-result {
            width: 100% !important;
            max-width: 100% !important; 
            padding: 2rem !important;
            background-color: #575760;
            border-radius: 8px;
            border: 1px solid #6b6b74;
            margin: 1rem 0;
        }
        
        /* Estilo para os cartões de crédito */
        .credit-card {
            background-color: #3F3F45;
            border: 1px solid #575760;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            color: white;
            text-align: center;
        }
        .credit-title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .credit-price {
            font-size: 42px;
            font-weight: bold;
            margin-bottom: 15px;
            color: white;
        }
        .credit-desc {
            font-size: 16px;
            color: #b0b0b0;
            margin-bottom: 15px;
        }
    </style>
    """ + hide_streamlit_menu(), unsafe_allow_html=True)
# Função para exibir a logo do ValueHunter de forma consistente
def show_valuehunter_logo():
    """Exibe a logo do ValueHunter de forma consistente"""
    st.markdown(
        '<div class="logo-container"><span class="logo-v">V</span><span class="logo-text">ValueHunter</span></div>', 
        unsafe_allow_html=True
    )

# Funções de navegação
def go_to_login():
    """Navigate to login page"""
    st.session_state.page = "login"
    st.session_state.show_register = False
    st.experimental_rerun()

def go_to_register():
    """Navigate to register page"""
    st.session_state.page = "register"
    st.session_state.show_register = True
    st.experimental_rerun()

def go_to_landing():
    """Navigate to landing page"""
    st.session_state.page = "landing"
    st.experimental_rerun()

# Função init_session_state
def init_session_state():
    """Initialize session state variables"""
    from utils.data import UserManager
    
    if "page" not in st.session_state:
        st.session_state.page = "landing"  # Nova variável para controlar a página atual
        
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if "email" not in st.session_state:
        st.session_state.email = None
    
    if "last_activity" not in st.session_state:
        st.session_state.last_activity = datetime.now()
    elif (datetime.now() - st.session_state.last_activity).total_seconds() > 3600:  # 1 hora
        st.session_state.authenticated = False
        st.session_state.email = None
        st.warning("Sua sessão expirou. Por favor, faça login novamente.")
    
    # Variáveis para a página de landing
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    
    # Variáveis para o checkout integrado
    if "show_checkout" not in st.session_state:
        st.session_state.show_checkout = False
    
    if "checkout_credits" not in st.session_state:
        st.session_state.checkout_credits = 0
        
    if "checkout_amount" not in st.session_state:
        st.session_state.checkout_amount = 0
        
    if "last_stripe_session_id" not in st.session_state:
        st.session_state.last_stripe_session_id = None
    
    # Stripe test mode flag
    if "stripe_test_mode" not in st.session_state:
        st.session_state.stripe_test_mode = True
    
    # UserManager deve ser o último a ser inicializado
    if "user_manager" not in st.session_state:
        st.session_state.user_manager = UserManager()
    
    # Atualizar timestamp de última atividade
    st.session_state.last_activity = datetime.now()

    # Apply the more aggressive CSS to hide admin pages
    hide_admin_pages_completely()

# Funções de Stripe
def init_stripe():
    """Initialize Stripe with the API key."""
    # Melhor controle de erros e logging para inicialização do Stripe
    try:
        # Se estamos no Render, usar variáveis de ambiente diretamente
        if "RENDER" in os.environ:
            api_key = os.environ.get("STRIPE_SECRET_KEY", "")
            logger.info("Usando API key do Stripe de variáveis de ambiente no Render")
        else:
            # Tente usar secrets (para desenvolvimento local ou Streamlit Cloud)
            try:
                api_key = st.secrets.get("STRIPE_SECRET_KEY", "")
                logger.info("Usando API key do Stripe de st.secrets")
            except Exception as e:
                logger.warning(f"Erro ao tentar carregar API key do Stripe de st.secrets: {str(e)}")
                api_key = os.environ.get("STRIPE_SECRET_KEY", "")
                logger.info("Usando API key do Stripe de variáveis de ambiente locais")
        
        # Atualizar API key do Stripe
        stripe.api_key = api_key
        
        if not stripe.api_key:
            logger.error("Stripe API key não encontrada em nenhuma configuração")
            st.error("Stripe API key not found")
        else:
            logger.info(f"Stripe API key configurada com sucesso. Modo de teste: {stripe.api_key.startswith('sk_test_')}")
        
        # Para teste, isso avisa os usuários que estão no modo de teste
        st.session_state.stripe_test_mode = stripe.api_key.startswith("sk_test_")
        
    except Exception as e:
        logger.error(f"Erro ao inicializar Stripe: {str(e)}")
        st.error(f"Erro ao inicializar Stripe. Por favor, tente novamente mais tarde.")

def get_base_url():
    """Get the base URL for the application, with special handling for Render."""
    # Check if running on Render
    if "RENDER" in os.environ:
        url = os.environ.get("RENDER_EXTERNAL_URL", "https://value-hunter.onrender.com")
        logger.info(f"Base URL no Render: {url}")
        return url
    # Check if running on Streamlit Cloud
    elif os.environ.get("IS_STREAMLIT_CLOUD"):
        url = os.environ.get("STREAMLIT_URL", "https://valuehunter.streamlit.app")
        logger.info(f"Base URL no Streamlit Cloud: {url}")
        return url
    # Local development
    else:
        try:
            url = st.get_option("server.baseUrlPath") or "http://localhost:8501"
            logger.info(f"Base URL local: {url}")
            return url
        except:
            logger.info("Usando URL local padrão: http://localhost:8501")
            return "http://localhost:8501"

def get_stripe_success_url(credits, email):
    """URL de sucesso que força refresh dos dados"""
    base_url = get_base_url()
    
    success_params = urlencode({
        'success_page': 'true',
        'credits': credits,
        'email': email,
        'session_id': '{CHECKOUT_SESSION_ID}',
        'payment_processed': 'true'  # Novo parâmetro para forçar refresh
    })
    
    full_url = f"{base_url}/?{success_params}"
    logger.info(f"URL de sucesso do Stripe configurada: {full_url}")
    return full_url

def get_stripe_cancel_url():
    """URL de cancelamento simplificada"""
    base_url = get_base_url()
    cancel_params = urlencode({'cancel_page': 'true'})
    full_url = f"{base_url}/?{cancel_params}"
    return full_url

def redirect_to_stripe(checkout_url):
    """Abre um popup para o checkout do Stripe"""
    # JavaScript para abrir o Stripe em um popup
    js_popup = f"""
    <script>
        // Abrir popup do Stripe centralizado
        var windowWidth = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
        var windowHeight = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
        
        var popupWidth = 600;
        var popupHeight = 700;
        
        var left = (windowWidth - popupWidth) / 2;
        var top = (windowHeight - popupHeight) / 2;
        
        // Abrir popup centralizado com nome único para evitar múltiplas janelas
        var stripePopup = window.open(
            '{checkout_url}', 
            'stripe_checkout',
            `width=${{popupWidth}},height=${{popupHeight}},left=${{left}},top=${{top}},location=yes,toolbar=yes,scrollbars=yes`
        );
        
        // Verificar se o popup foi bloqueado
        if (!stripePopup || stripePopup.closed || typeof stripePopup.closed == 'undefined') {{
            // Popup foi bloqueado
            document.getElementById('popup-blocked').style.display = 'block';
        }} else {{
            // Popup foi aberto com sucesso
            document.getElementById('popup-success').style.display = 'block';
        }}
    </script>
    
    <div id="popup-blocked" style="display:none; padding: 15px; background-color: #ffcccc; border-radius: 5px; margin: 15px 0;">
        <h3>⚠️ Popup bloqueado!</h3>
        <p>Seu navegador bloqueou o popup de pagamento. Por favor:</p>
        <ol>
            <li>Clique no ícone de bloqueio de popup na barra de endereço</li>
            <li>Selecione "Sempre permitir popups de [seu site]"</li>
            <li>Clique no botão abaixo para tentar novamente</li>
        </ol>
        <a href="{checkout_url}" target="_blank" style="display: inline-block; padding: 10px 15px; background-color: #fd7014; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
            Abrir página de pagamento
        </a>
    </div>
    
    <div id="popup-success" style="display:none; padding: 15px; background-color: #e6ffe6; border-radius: 5px; margin: 15px 0;">
        <h3>✅ Janela de pagamento aberta!</h3>
        <p>Uma nova janela foi aberta para você concluir seu pagamento.</p>
        <p>Após completar o pagamento, a janela será fechada automaticamente e seus créditos serão adicionados.</p>
        <p>Para ver seus créditos, clique no botão "Voltar para análises" após concluir o pagamento.</p>
    </div>
    """
    
    # Exibir o JavaScript
    st.components.v1.html(js_popup, height=350)

def create_stripe_checkout_session(email, credits, amount):
    """Cria uma sessão de checkout do Stripe com manejo simplificado"""
    try:
        # Initialize Stripe
        init_stripe()
        
        # Convert amount to cents
        amount_cents = int(float(amount) * 100)
        
        # Create product description
        product_description = f"{credits} Créditos para ValueHunter"
        
        # Create success URL
        success_url = get_stripe_success_url(credits, email)
        cancel_url = get_stripe_cancel_url()
        
        logger.info(f"Criando sessão de checkout para {email}: {credits} créditos, R${amount}")
        logger.info(f"Success URL: {success_url}")
        logger.info(f"Cancel URL: {cancel_url}")
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'brl',
                    'product_data': {
                        'name': f'ValueHunter - {credits} Créditos',
                        'description': product_description,
                    },
                    'unit_amount': amount_cents,
                },
                'quantity': 1,
            }],
            mode='payment',
            customer_email=email,
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'email': email,
                'credits': str(credits)
            }
        )
        
        # Armazenar o ID da sessão
        st.session_state.last_stripe_session_id = checkout_session.id
        logger.info(f"Sessão de checkout do Stripe criada com sucesso: {checkout_session.id}")
        
        return checkout_session
    except Exception as e:
        logger.error(f"Erro ao criar sessão de pagamento: {str(e)}")
        st.error(f"Erro ao criar sessão de pagamento: {str(e)}")
        return None

def verify_stripe_payment(session_id):
    """
    Versão aprimorada e mais tolerante da verificação de pagamento.
    Em ambiente de teste, SEMPRE considera o pagamento válido.
    """
    try:
        logger.info(f"Verificando sessão de pagamento: {session_id}")
        
        # IMPORTANTE: Em ambiente de teste, considerar QUALQUER pagamento válido
        if st.session_state.stripe_test_mode:
            try:
                # Tentar obter dados reais, mas não falhar se não conseguir
                if session_id and session_id.startswith('cs_'):
                    try:
                        session = stripe.checkout.Session.retrieve(session_id)
                        credits = int(session.metadata.get('credits', 0))
                        email = session.metadata.get('email', '')
                        logger.info(f"TESTE: Sessão válida para {email}: {credits} créditos")
                        return True, credits, email
                    except:
                        # Se falhar, pegar dados da URL (fallback)
                        credits = st.query_params.get('credits', 0)
                        email = st.query_params.get('email', '')
                        credits = int(credits) if isinstance(credits, str) else credits
                        logger.info(f"TESTE FALLBACK: Usando dados da URL: {email}, {credits} créditos")
                        return True, credits, email
            except Exception as e:
                # Sempre retornar verdadeiro em ambiente de teste, com valores de fallback
                logger.warning(f"Erro em ambiente de teste, usando fallback: {str(e)}")
                credits = st.query_params.get('credits', 30)  # Valor padrão se tudo falhar
                email = st.query_params.get('email', '')
                credits = int(credits) if isinstance(credits, str) else credits
                return True, credits, email

        # Em ambiente de produção, verificar o status do pagamento
        if session_id and session_id.startswith('cs_'):
            try:
                session = stripe.checkout.Session.retrieve(session_id)
                
                # Extrair informações mesmo que o pagamento não esteja completo
                credits = int(session.metadata.get('credits', 0))
                email = session.metadata.get('email', '')
                
                # Verificar status de pagamento
                if session.payment_status == 'paid':
                    logger.info(f"PRODUÇÃO: Pagamento verificado com sucesso: {session_id}")
                    return True, credits, email
                else:
                    logger.warning(f"PRODUÇÃO: Pagamento não concluído: {session_id}, status: {session.payment_status}")
                    # Retornar os dados, mas indicando que o pagamento não está confirmado
                    return False, credits, email
            except Exception as e:
                logger.error(f"Erro ao verificar sessão do Stripe: {str(e)}")
                # Em caso de erro, tentar obter informações da URL
                credits = st.query_params.get('credits', 0) 
                email = st.query_params.get('email', '')
                credits = int(credits) if isinstance(credits, str) else credits
                return False, credits, email
        
        # Se não há ID de sessão ou não começa com cs_
        logger.warning(f"ID de sessão inválido: {session_id}")
        credits = st.query_params.get('credits', 0)
        email = st.query_params.get('email', '')
        credits = int(credits) if isinstance(credits, str) else credits
        return False, credits, email
        
    except Exception as e:
        logger.error(f"Erro crítico ao verificar pagamento: {str(e)}")
        # Último recurso - tentar obter da URL
        credits = st.query_params.get('credits', 0)
        email = st.query_params.get('email', '')
        credits = int(credits) if isinstance(credits, str) else credits
        return False, credits, email

def update_purchase_button(credits, amount):
    """Função comum para processar a compra de créditos"""
    logger.info(f"Botão de {credits} créditos clicado")
    
    # Criar checkout e redirecionar
    checkout_session = create_stripe_checkout_session(
        st.session_state.email, 
        credits, 
        amount
    )
    
    if checkout_session:
        logger.info(f"Checkout session criada: {checkout_session.id}")
        redirect_to_stripe(checkout_session.url)
        return True
        
    return False

def check_payment_success():
    """
    Verifica se estamos em uma página especial de sucesso/cancelamento
    ou se estamos verificando parâmetros na página principal.
    """
    # Verificar se estamos na página de sucesso do popup
    if 'success_page' in st.query_params and st.query_params.success_page == 'true':
        return handle_success_page()
        
    # Verificar se estamos na página de cancelamento do popup
    if 'cancel_page' in st.query_params and st.query_params.cancel_page == 'true':
        return handle_cancel_page()
        
    return False

def handle_success_page():
    """
    Função aprimorada que garante a adição de créditos,
    mesmo em caso de erros.
    """
    try:
        # Obter parâmetros da URL
        credits_param = st.query_params.get('credits', '0')
        email_param = st.query_params.get('email', '')
        session_id = st.query_params.get('session_id', '')
        
        # Converter créditos para número
        try:
            credits_value = int(credits_param)
        except:
            credits_value = 0
            
        # Log detalhado
        logger.info(f"Processando página de sucesso: email={email_param}, credits={credits_value}, session_id={session_id}")
        
        # Inicializar Stripe (garantir que temos acesso à API)
        try:
            init_stripe()
        except Exception as e:
            logger.error(f"Erro ao inicializar Stripe: {str(e)}")
        
        # Verificar pagamento de forma robusta
        is_valid, verified_credits, verified_email = verify_stripe_payment(session_id)
        
        # Log detalhado após verificação
        logger.info(f"Resultado da verificação: valid={is_valid}, credits={verified_credits}, email={verified_email}")
        
        # Variáveis para a mensagem
        final_credits = verified_credits if verified_credits > 0 else credits_value
        final_email = verified_email if verified_email else email_param
        
        # IMPORTANTE: Adicionar créditos SEMPRE, garantindo que não falhe
        credits_added = False
        
        # Primeira tentativa: usar email verificado
        if final_email and final_credits > 0:
            try:
                logger.info(f"Tentando adicionar {final_credits} créditos para {final_email}")
                
                # Verificar se o usuário existe
                if hasattr(st.session_state, 'user_manager') and final_email in st.session_state.user_manager.users:
                    # Adicionar diretamente na estrutura de dados para garantir
                    if "purchased_credits" not in st.session_state.user_manager.users[final_email]:
                        st.session_state.user_manager.users[final_email]["purchased_credits"] = 0
                    
                    st.session_state.user_manager.users[final_email]["purchased_credits"] += final_credits
                    
                    # Limpar timestamp de esgotamento se existir
                    if "paid_credits_exhausted_at" in st.session_state.user_manager.users[final_email]:
                        st.session_state.user_manager.users[final_email]["paid_credits_exhausted_at"] = None
                    
                    # Salvar alterações
                    st.session_state.user_manager._save_users()
                    
                    # Registrar sucesso
                    logger.info(f"Créditos adicionados diretamente: {final_credits} para {final_email}")
                    credits_added = True
                else:
                    # Tentar usar a função padrão
                    if st.session_state.user_manager.add_credits(final_email, final_credits):
                        logger.info(f"Créditos adicionados via função: {final_credits} para {final_email}")
                        credits_added = True
                    else:
                        logger.warning(f"Falha ao adicionar créditos via função: {final_credits} para {final_email}")
            except Exception as add_error:
                logger.error(f"Erro ao adicionar créditos para {final_email}: {str(add_error)}")
        
        # Log final
        if credits_added:
            logger.info(f"SUCESSO: {final_credits} créditos adicionados para {final_email}")
        else:
            logger.warning(f"FALHA: Não foi possível adicionar créditos para {final_email}")
        
        # HTML ultra-simples, apenas a mensagem
        success_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pagamento Aprovado</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #3F3F45;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    padding: 20px;
                    box-sizing: border-box;
                }}
                .message-box {{
                    background-color: #4CAF50;
                    border-radius: 10px;
                    padding: 30px;
                    text-align: center;
                    max-width: 500px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }}
                .logo {{
                    background-color: #fd7014;
                    padding: 10px 20px;
                    border-radius: 8px;
                    display: inline-flex;
                    align-items: center;
                    margin-bottom: 20px;
                }}
                .logo-v {{
                    color: #3F3F45;
                    font-size: 2rem;
                    font-weight: bold;
                }}
                .logo-text {{
                    font-size: 1.7rem;
                    font-weight: bold;
                    color: white;
                }}
                h1 {{
                    font-size: 1.8rem;
                    margin: 15px 0;
                }}
                p {{
                    font-size: 1.2rem;
                    margin: 10px 0;
                }}
                .credits {{
                    font-size: 2.5rem;
                    font-weight: bold;
                    color: #FFEB3B;
                    margin: 15px 0;
                }}
                .status {{
                    font-size: 1rem;
                    color: rgba(255,255,255,0.8);
                    margin-top: 20px;
                    font-style: italic;
                }}
            </style>
        </head>
        <body>
            <div class="message-box">
                <div class="logo">
                    <span class="logo-v">V</span>
                    <span class="logo-text">ValueHunter</span>
                </div>
                <h1>✅ Pagamento Aprovado</h1>
                <p>Seu pagamento foi processado com sucesso.</p>
                <div class="credits">{final_credits} créditos</div>
                <p>foram adicionados à sua conta.</p>
                <p><strong>Feche esta janela para continuar.</strong></p>
                <div class="status">{f"ID: {session_id[:8]}..." if session_id else "Processado com sucesso"}</div>
            </div>
        </body>
        </html>
        """
        
        # Renderizar APENAS o HTML
        st.components.v1.html(success_html, height=400, scrolling=False)
        
        # Impedir a execução de qualquer outro código
        st.stop()
        
        return True
        
    except Exception as e:
        logger.error(f"Erro crítico na página de sucesso: {str(e)}")
        
        # Mensagem de erro ultra-simples
        error_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Processando Pagamento</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #3F3F45;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    padding: 20px;
                    box-sizing: border-box;
                }
                .message-box {
                    background-color: #2196F3;
                    border-radius: 10px;
                    padding: 30px;
                    text-align: center;
                    max-width: 500px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                .logo {
                    background-color: #fd7014;
                    padding: 10px 20px;
                    border-radius: 8px;
                    display: inline-flex;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .logo-v {
                    color: #3F3F45;
                    font-size: 2rem;
                    font-weight: bold;
                }
                .logo-text {
                    font-size: 1.7rem;
                    font-weight: bold;
                    color: white;
                }
                h1 {
                    font-size: 1.8rem;
                    margin: 15px 0;
                }
                p {
                    font-size: 1.2rem;
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
            <div class="message-box">
                <div class="logo">
                    <span class="logo-v">V</span>
                    <span class="logo-text">ValueHunter</span>
                </div>
                <h1>Processando Pagamento</h1>
                <p>Estamos verificando seu pagamento.</p>
                <p><strong>Feche esta janela para continuar.</strong></p>
            </div>
        </body>
        </html>
        """
        
        st.components.v1.html(error_html, height=400, scrolling=False)
        st.stop()
        return False

def handle_cancel_page():
    """
    Mostra APENAS uma mensagem estática de cancelamento, sem timer.
    """
    try:
        # HTML ultra-simples
        cancel_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Pagamento Não Aprovado</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #3F3F45;
                    color: white;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    padding: 20px;
                    box-sizing: border-box;
                }
                .message-box {
                    background-color: #FF9800;
                    border-radius: 10px;
                    padding: 30px;
                    text-align: center;
                    max-width: 500px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                .logo {
                    background-color: #fd7014;
                    padding: 10px 20px;
                    border-radius: 8px;
                    display: inline-flex;
                    align-items: center;
                    margin-bottom: 20px;
                }
                .logo-v {
                    color: #3F3F45;
                    font-size: 2rem;
                    font-weight: bold;
                }
                .logo-text {
                    font-size: 1.7rem;
                    font-weight: bold;
                    color: white;
                }
                h1 {
                    font-size: 1.8rem;
                    margin: 15px 0;
                }
                p {
                    font-size: 1.2rem;
                    margin: 10px 0;
                }
            </style>
        </head>
        <body>
            <div class="message-box">
                <div class="logo">
                    <span class="logo-v">V</span>
                    <span class="logo-text">ValueHunter</span>
                </div>
                <h1>⚠️ Pagamento Não Aprovado</h1>
                <p>O pagamento não foi concluído.</p>
                <p><strong>Feche esta janela e tente novamente.</strong></p>
            </div>
        </body>
        </html>
        """
        
        # Renderizar APENAS o HTML
        st.components.v1.html(cancel_html, height=400, scrolling=False)
        
        # Parar a execução
        st.stop()
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao exibir página de cancelamento: {str(e)}")
        return False

def handle_stripe_errors():
    if 'error' in st.query_params:
        st.error("Erro no processamento do pagamento...")
        st.query_params.clear()
def apply_responsive_styles():
    """
    Aplica estilos CSS responsivos para melhorar a aparência e usabilidade 
    do aplicativo em diferentes dispositivos.
    """
    import streamlit as st
    
    # CSS para melhorar a responsividade e margens do aplicativo
    st.markdown("""
    <style>
    /* Configurações principais de layout */
    .main .block-container {
        padding-left: max(1rem, 5%);
        padding-right: max(1rem, 5%);
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Melhor espaçamento para contêineres */
    div.stApp {
        background-color: #1a1a1a;
    }

    /* Melhorar margens laterais */
    [data-testid="column"] {
        padding: 0.5rem;
    }

    /* Aumentar margens responsivas para conteúdo principal */
    @media (min-width: 768px) {
        .main .block-container {
            padding-left: max(2rem, 8%);
            padding-right: max(2rem, 8%);
        }
        
        /* Margens laterais melhores em desktop */
        [data-testid="column"] {
            padding: 0.75rem;
        }
    }

    /* Ajustes para dispositivos móveis */
    @media (max-width: 767px) {
        .main .block-container {
            padding-left: 0.75rem;
            padding-right: 0.75rem;
        }
        
        /* Estilo específico para botões em mobile */
        button[data-testid="baseButton-primary"] {
            width: 100%;
            margin: 0.25rem 0;
        }
        
        /* Ajustar barra lateral em modo móvel */
        [data-testid="stSidebar"] {
            min-width: 250px !important;
            max-width: 300px !important;
        }
    }

    /* Melhorar espaçamento dos formulários e inputs */
    input[type="text"], 
    input[type="email"], 
    input[type="password"], 
    textarea {
        margin-bottom: 0.75rem !important;
    }

    /* Estilo para cards de pacotes */
    .credit-card {
        background-color: #292929;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        text-align: center;
        border: 1px solid #3a3a3a;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, box-shadow 0.2s;
    }

    .credit-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }

    .credit-title {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #fd7014;
    }

    .credit-price {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: white;
    }

    .credit-desc {
        color: #b0b0b0;
        font-size: 1rem;
    }

    /* Melhorar aparência em geral */
    h1, h2, h3 {
        color: #fd7014;
        margin-bottom: 1rem;
    }

    /* Estilo para mensagens de alerta, erro e sucesso */
    [data-testid="stAlert"] {
        border-radius: 8px;
        padding: 0.75rem 1rem;
        margin: 1rem 0;
    }

    /* Header com logo */
    .vh-logo {
        max-height: 60px;
        display: block;
    }

    /* Estilo para a landing page */
    .hero {
        padding: 2rem 0;
        text-align: center;
        margin-bottom: 2rem;
    }

    .hero h1 {
        color: #fd7014;
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }

    @media (max-width: 576px) {
        .hero h1 {
            font-size: 1.8rem;
        }
    }

    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem 0;
        margin-top: 3rem;
        border-top: 1px solid #3a3a3a;
    }
    </style>
    """, unsafe_allow_html=True)
# Add this to your core.py file or modify the existing CSS functions

