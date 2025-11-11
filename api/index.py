import os
import sys
import logging

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar o diretório raiz ao path para imports
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

logger.info(f"Root directory: {root_dir}")
logger.info(f"Python path: {sys.path}")

try:
    from app import app
    
    # Ajustar configurações para ambiente serverless da Vercel
    # A Vercel usa HTTPS, mas precisamos garantir que as configurações estejam corretas
    app.config['SESSION_COOKIE_SECURE'] = os.environ.get('VERCEL_ENV') == 'production'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    logger.info("Flask app imported successfully")
    logger.info(f"Templates folder: {app.template_folder}")
    logger.info(f"Static folder: {app.static_folder}")
    
    # A Vercel espera um objeto 'app' ou 'application' como WSGI application
    # O Flask app já é um WSGI application válido
    application = app
    
except Exception as e:
    logger.error(f"Error importing app: {str(e)}", exc_info=True)
    raise

# Para compatibilidade local
if __name__ == '__main__':
    app.run()

