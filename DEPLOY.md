# 🚀 Guia de Deploy no Streamlit Cloud

Este guia mostra como fazer o deploy do Dashboard RDA THS no Streamlit Cloud (gratuito).

---

## 📋 Pré-requisitos

✅ **Conta no GitHub** (crie em: https://github.com/signup)  
✅ **Conta no Streamlit Cloud** (crie em: https://share.streamlit.io/signup)  
✅ **Git instalado** (baixe em: https://git-scm.com/downloads)

---

## 🔧 Passo 1: Instalar o Git (se ainda não tiver)

1. Baixe o Git: https://git-scm.com/downloads
2. Instale com as opções padrão
3. Reinicie o terminal/PowerShell
4. Teste executando: `git --version`

---

## 📤 Passo 2: Subir o Projeto para o GitHub

### Opção A: Via GitHub Desktop (Mais Fácil)

1. **Baixe o GitHub Desktop**: https://desktop.github.com/
2. **Instale e faça login** com sua conta GitHub
3. **Clique em** "File" → "Add Local Repository"
4. **Selecione a pasta**: `C:\Users\gabriel.antonio\Desktop\Antigravity\Projeto Dashboard`
5. **Clique em** "Create a repository" (se aparecer)
6. **Configure**:
   - Nome: `dashboard-petrobras` (ou outro nome)
   - Descrição: "Dashboard RDA THS - PETROBRAS"
   - ✅ Marque "Private" (se quiser manter privado)
7. **Clique em** "Publish repository"

### Opção B: Via Linha de Comando (Terminal)

Abra o PowerShell na pasta do projeto e execute:

```powershell
# Entre na pasta do projeto
cd "C:\Users\gabriel.antonio\Desktop\Antigravity\Projeto Dashboard"

# Inicialize o Git
git init

# Adicione todos os arquivos
git add .

# Faça o primeiro commit
git commit -m "Deploy inicial do Dashboard RDA THS"

# Crie um repositório no GitHub primeiro (via navegador)
# Depois conecte com:
git remote add origin https://github.com/SEU-USUARIO/SEU-REPO.git

# Envie para o GitHub
git branch -M main
git push -u origin main
```

---

## ☁️ Passo 3: Deploy no Streamlit Cloud

1. **Acesse**: https://share.streamlit.io/
2. **Faça login** com sua conta GitHub
3. **Clique em** "New app"
4. **Configure**:
   - **Repository**: Selecione o repositório que você criou
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Escolha um nome (ex: `dashboard-petrobras`)
5. **Clique em** "Deploy!"

⏱️ **Aguarde 2-5 minutos** para o deploy ser concluído.

---

## ✅ Passo 4: Testar o Deploy

Após o deploy, você receberá um link como:

🔗 `https://dashboard-petrobras-SEU-USUARIO.streamlit.app`

**Teste**:
1. Abra o link no navegador
2. Faça upload de um arquivo Excel de teste
3. Verifique se os filtros funcionam
4. Teste adicionar observações

---

## 🔄 Como Atualizar o App Após Mudanças

### Via GitHub Desktop:
1. Faça suas alterações no código
2. Abra o GitHub Desktop
3. Escreva uma mensagem de commit
4. Clique em "Commit to main"
5. Clique em "Push origin"

### Via Terminal:
```bash
git add .
git commit -m "Descrição da mudança"
git push
```

**O Streamlit Cloud atualiza automaticamente em ~1-2 minutos!** 🚀

---

## 🔒 Tornando o Repositório Privado

Se você não marcou como privado no início:

1. Vá para: `https://github.com/SEU-USUARIO/SEU-REPO/settings`
2. Role até "Danger Zone"
3. Clique em "Change visibility" → "Make private"

---

## ⚙️ Configurações Avançadas (Opcional)

### Limites de Recursos

O plano gratuito inclui:
- 1 GB de RAM
- 1 CPU compartilhado
- Ilimitado de apps públicos
- 1 app privado

### Variáveis de Ambiente (Secrets)

Se precisar de senhas ou tokens:

1. No Streamlit Cloud, clique em "Settings"
2. Vá em "Secrets"
3. Adicione no formato TOML:

```toml
[passwords]
admin_password = "sua_senha_aqui"
```

---

## 🆘 Solução de Problemas

### ❌ Erro: "ModuleNotFoundError"
**Solução**: Verifique se todas as bibliotecas estão no `requirements.txt`

### ❌ Erro: "File not found: app.py"
**Solução**: Confirme que o arquivo principal se chama exatamente `app.py`

### ❌ App muito lento
**Solução**: Otimize o código usando `@st.cache_data` para operações pesadas

### ❌ Repositório privado não aparece
**Solução**: Dê permissão ao Streamlit nas configurações do GitHub:
- GitHub → Settings → Applications → Streamlit → Configure

---

## 📞 Suporte

- **Documentação Streamlit**: https://docs.streamlit.io/
- **Comunidade**: https://discuss.streamlit.io/
- **Status**: https://streamlit.statuspage.io/

---

## 🎉 Próximos Passos

Após o deploy bem-sucedido:

1. ✅ Compartilhe o link com sua equipe
2. ✅ Atualize o README.md com o link correto
3. ✅ Configure notificações de erro (se necessário)
4. ✅ Considere adicionar autenticação para dados sensíveis

**Bom deploy! 🚀**
