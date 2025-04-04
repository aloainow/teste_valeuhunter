# app.py - Arquivo principal (ponto de entrada)
import os
import logging
import sys
import streamlit as st
from datetime import datetime

# Initialize session state variables (no Streamlit commands here, just dictionary operations)
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "email" not in st.session_state:
    st.session_state.email = None
if "show_register" not in st.session_state:
    st.session_state.show_register = False
# (other session state initializations)

# Importar módulos de utilidade
from utils.core import (
    DATA_DIR, init_session_state, show_valuehunter_logo, 
    configure_sidebar_visibility, apply_global_css, init_stripe,
    check_payment_success, handle_stripe_errors, hide_admin_pages_completely
)
from utils.data import UserManager

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("valueHunter")

# Log de diagnóstico no início
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
try:
    logger.info(f"Directory contents: {os.listdir('.')}")
except Exception as e:
    logger.error(f"Erro ao listar diretório: {str(e)}")

# Criar diretório de dados se não existir
os.makedirs(DATA_DIR, exist_ok=True)
logger.info(f"Diretório de dados configurado: {DATA_DIR}")
logger.info(f"Conteúdo do diretório de dados: {os.listdir(DATA_DIR) if os.path.exists(DATA_DIR) else 'Diretório não existe'}")

# THIS MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="ValueHunter - Análise de Apostas Esportivas",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Now you can run other Streamlit commands
hide_admin_pages_completely()

# Add the JavaScript component AFTER set_page_config
st.components.v1.html("""
<script>
// Function to hide specific sidebar items
function hideAdminItems() {
    // Target the sidebar items
    const allItems = document.querySelectorAll('div[role="listitem"] a, [data-testid="stSidebarNavItems"] a, li a');
    
    // Loop through all items and hide ones containing app or admin
    allItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        const href = item.getAttribute('href') || '';
        
        if (text === 'app' || text === 'admin' || 
            href.includes('app') || href.includes('admin')) {
            // Hide the parent list item
            const parent = item.closest('li') || item.closest('div[role="listitem"]') || item;
            if (parent) parent.style.display = 'none';
        }
    });
    
    // Also try to hide the dropdown items
    const dropdownItems = document.querySelectorAll('div[role="menu"] p, div[role="menu"] a');
    dropdownItems.forEach(item => {
        const text = item.textContent.toLowerCase();
        if (text === 'app' || text === 'admin') {
            const parent = item.closest('a') || item.closest('div') || item;
            if (parent) parent.style.display = 'none';
        }
    });
}

// Execute immediately
hideAdminItems();

// Also set up an observer to hide items when new elements are added
const observer = new MutationObserver((mutations) => {
    hideAdminItems();
});

// Start observing the sidebar and dialog areas
setTimeout(() => {
    const sidebar = document.querySelector('[data-testid="stSidebar"]');
    const body = document.body;
    
    if (sidebar) {
        observer.observe(sidebar, { childList: true, subtree: true });
    }
    
    observer.observe(body, { childList: true, subtree: true });
    
    // Run every half second for the first few seconds
    let count = 0;
    const interval = setInterval(() => {
        hideAdminItems();
        count++;
        if (count > 10) clearInterval(interval);
    }, 500);
}, 100);
</script>
""", height=0)

# Ocultar o próprio app.py do menu de navegação e qualquer elemento do menu
st.markdown("""
<style>
/* Your existing CSS here */
</style>
""", unsafe_allow_html=True)

# Importar e disponibilizar funções e classes principais
from utils.core import (
    go_to_login, go_to_register, go_to_landing,
    get_base_url, redirect_to_stripe, update_purchase_button
)
from pages.dashboard import show_main_dashboard
from pages.landing import show_landing_page
from pages.auth import show_login, show_register
from pages.packages import show_packages_page

# Defina esta função FORA da função main
def enable_debug_mode():
    """Ativa o modo de debug para ajudar na resolução de problemas"""
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
        
    # Verificar se o modo de debug deve ser ativado
    if st.sidebar.checkbox("Modo de Debug", value=st.session_state.debug_mode):
        st.session_state.debug_mode = True
        st.session_state.use_sample_data = True
        
        st.sidebar.success("Modo de debug ativado")
        
        # Exibir informações de debug
        if st.sidebar.checkbox("Mostrar informações do sistema"):
            st.sidebar.subheader("Informações do Sistema")
            st.sidebar.info(f"Python: {sys.version}")
            st.sidebar.info(f"Diretório: {os.getcwd()}")
            st.sidebar.info(f"DATA_DIR: {DATA_DIR}")
            
        # Exibir logs recentes
        if st.sidebar.checkbox("Mostrar logs recentes"):
            st.sidebar.subheader("Logs Recentes")
            try:
                log_file = "valueHunter.log"
                if os.path.exists(log_file):
                    with open(log_file, "r") as f:
                        logs = f.readlines()[-20:]  # Últimas 20 linhas
                    for log in logs:
                        st.sidebar.text(log.strip())
                else:
                    st.sidebar.warning("Arquivo de log não encontrado")
            except Exception as e:
                st.sidebar.error(f"Erro ao ler logs: {str(e)}")
        
        # Ativar dados de exemplo
        st.session_state.use_sample_data = st.sidebar.checkbox(
            "Usar dados de exemplo", 
            value=st.session_state.get("use_sample_data", True)
        )
        
        # Permitir forçar reload do cache
        if st.sidebar.button("Limpar cache"):
            import glob
            cache_files = glob.glob(os.path.join(DATA_DIR, "cache_*.html"))
            for f in cache_files:
                try:
                    os.remove(f)
                    st.sidebar.success(f"Removido: {os.path.basename(f)}")
                except Exception as e:
                    st.sidebar.error(f"Erro ao remover {f}: {str(e)}")
    else:
        st.session_state.debug_mode = False

# Agora a função main, com sua estrutura corrigida
def main():
    try:
        # Verificar se precisamos fechar a janela atual
        if 'close_window' in st.query_params and st.query_params.close_window == 'true':
            st.components.v1.html("""
                <script>
                    window.opener && window.opener.postMessage('payment_complete', '*');
                    window.close();
                </script>
            """, height=0)
            st.success("Pagamento concluído! Você pode fechar esta janela.")
            return
            
        # Initialize session state
        init_session_state()
        
        # Configurar visibilidade da barra lateral
        configure_sidebar_visibility()
        
        # Apply global CSS
        apply_global_css()
        
        # Initialize Stripe
        init_stripe()

        # Apply the CSS immediately at app start
        hide_admin_pages_completely()

        # Check for payment from popup
        popup_payment = False
        if 'check_payment' in st.query_params and st.query_params.check_payment == 'true':
            popup_payment = True
        
        # Handle page routing
        if popup_payment and st.session_state.authenticated:
            check_payment_success()
            
        # Regular payment callback check
        payment_result = check_payment_success()
        
        # Stripe error handling
        handle_stripe_errors()
        
        # Roteamento de páginas
        route_pages()
        
    except Exception as e:
        logger.error(f"Erro geral na aplicação: {str(e)}")
        import traceback
        traceback.print_exc()

def route_pages():
    if st.session_state.page == "landing":
        show_landing_page()
    elif st.session_state.page == "login":
        show_login()
    elif st.session_state.page == "register":
        show_register()
    elif st.session_state.page == "main":
        if not st.session_state.authenticated:
            st.warning("Sua sessão expirou. Por favor, faça login novamente.")
            go_to_login()
            return
        show_main_dashboard()
    elif st.session_state.page == "packages":
        if not st.session_state.authenticated:
            st.warning("Você precisa fazer login para acessar os pacotes.")
            go_to_login()
            return
        show_packages_page()
    else:
        st.session_state.page = "landing"
        st.experimental_rerun()

# Executar a aplicação
if __name__ == "__main__":
    try:
        logger.info("Iniciando aplicação ValueHunter")
        main()
    except Exception as e:
        logger.critical(f"Erro fatal na aplicação: {str(e)}")
        st.error("Ocorreu um erro inesperado. Por favor, recarregue a página e tente novamente.")
        st.error(f"Detalhes do erro: {str(e)}")
