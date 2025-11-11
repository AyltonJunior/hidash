import os
import sys

# Adicionar o diretório raiz ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

# Ajustar configurações para ambiente serverless da Vercel
# A Vercel usa HTTPS, mas precisamos garantir que as configurações estejam corretas
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('VERCEL_ENV') == 'production'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# A Vercel espera um objeto 'app' ou 'application' como WSGI application
# O Flask app já é um WSGI application válido
application = app

# Para compatibilidade local
if __name__ == '__main__':
    app.run()

