# Configuração para Deploy na Vercel

## Variáveis de Ambiente Necessárias

Configure as seguintes variáveis de ambiente no painel da Vercel:

1. **DATABASE_URL**: URL de conexão do PostgreSQL
   - Formato: `postgresql://usuario:senha@host:porta/database`
   - Exemplo: `postgresql://user:pass@host:5432/dbname`

2. **SESSION_SECRET**: Chave secreta para sessões (opcional, mas recomendado)
   - Gere uma chave aleatória segura
   - Exemplo: `python -c "import secrets; print(secrets.token_hex(32))"`

## Estrutura de Arquivos

- `api/index.py`: Função serverless que serve a aplicação Flask
- `vercel.json`: Configuração de rotas e builds
- `requirements.txt`: Dependências Python

## Notas Importantes

1. **Database**: Certifique-se de que o banco de dados PostgreSQL está acessível da Vercel
2. **Migrations**: As tabelas serão criadas automaticamente na primeira execução se `DATABASE_URL` estiver configurado
3. **Sessões**: As configurações de sessão foram ajustadas para funcionar corretamente na Vercel
4. **Arquivos Estáticos**: Os arquivos em `/static` são servidos diretamente pela Vercel

## Deploy

1. Faça commit das mudanças
2. Faça push para o repositório conectado à Vercel
3. A Vercel fará o deploy automaticamente

## Troubleshooting

Se ainda houver erros:
1. Verifique os logs na Vercel Dashboard
2. Certifique-se de que `DATABASE_URL` está configurado corretamente
3. Verifique se todas as dependências estão no `requirements.txt`

