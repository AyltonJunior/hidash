# Configuração para Deploy na Vercel

## Variáveis de Ambiente Necessárias

Configure as seguintes variáveis de ambiente no painel da Vercel:

1. **DATABASE_URL**: URL de conexão do PostgreSQL (OBRIGATÓRIO)
   - Formato: `postgresql://usuario:senha@host:porta/database`
   - Exemplo: `postgresql://user:pass@host:5432/dbname`
   - **IMPORTANTE**: Sem esta variável, a aplicação não funcionará!

2. **SESSION_SECRET**: Chave secreta para sessões (opcional, mas recomendado)
   - Gere uma chave aleatória segura
   - Exemplo: `python -c "import secrets; print(secrets.token_hex(32))"`

## Estrutura de Arquivos

- `api/index.py`: Função serverless que serve a aplicação Flask
- `vercel.json`: Configuração de rotas e builds
- `requirements.txt`: Dependências Python

## Mudanças Realizadas

1. ✅ Criado `api/index.py` com tratamento de erros melhorado
2. ✅ Configurados caminhos absolutos para templates e static files
3. ✅ Ajustado pool de conexões do banco para serverless
4. ✅ Melhorado tratamento de erros na inicialização
5. ✅ Removida especificação de Python 3.11 (usa 3.12 automaticamente)

## Notas Importantes

1. **Database**: Certifique-se de que o banco de dados PostgreSQL está acessível da Vercel
2. **Migrations**: As tabelas serão criadas automaticamente na primeira execução se `DATABASE_URL` estiver configurado
3. **Sessões**: As configurações de sessão foram ajustadas para funcionar corretamente na Vercel
4. **Arquivos Estáticos**: Os arquivos em `/static` são servidos diretamente pela Vercel
5. **Python Version**: A Vercel está usando Python 3.12 (o aviso é apenas informativo)

## Deploy

1. Faça commit das mudanças
2. Faça push para o repositório conectado à Vercel
3. A Vercel fará o deploy automaticamente

## Troubleshooting

### Erro: FUNCTION_INVOCATION_FAILED

Se ainda houver erros após o deploy:

1. **Verifique os logs na Vercel Dashboard**
   - Vá em "Deployments" > Selecione o deployment > "Functions" > Clique na função
   - Os logs mostrarão o erro exato

2. **Verifique se DATABASE_URL está configurado**
   - Vá em "Settings" > "Environment Variables"
   - Certifique-se de que `DATABASE_URL` está definido para Production, Preview e Development

3. **Verifique a conexão com o banco**
   - Teste a URL de conexão localmente
   - Certifique-se de que o banco aceita conexões externas (se necessário)

4. **Verifique os logs de build**
   - Os avisos sobre Python 3.11 são normais (usa 3.12)
   - O aviso sobre `builds` no vercel.json também é normal

### Erros Comuns

- **"No module named 'app'"**: Verifique se todos os arquivos estão no repositório
- **"Template not found"**: Os caminhos foram configurados automaticamente
- **"Database connection failed"**: Verifique `DATABASE_URL` e conectividade do banco

## Próximos Passos

Após o deploy bem-sucedido:
1. Acesse a URL fornecida pela Vercel
2. Se necessário, execute `init_db.py` localmente para criar dados iniciais
3. Faça login com as credenciais criadas


