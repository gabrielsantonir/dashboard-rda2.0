# 📊 Dashboard RDA THS - PETROBRAS

Dashboard interativo para consulta diária de dados de coletas e entregas.

🔗 **[Acesse o Dashboard Online](https://SEU-LINK-AQUI.streamlit.app)** _(atualizar após deploy)_

---

## ✨ Funcionalidades

- ✅ **Upload de Excel**: Importa arquivo com abas "coletas" e "entregas"
- 🔍 **Filtros Inteligentes**: Data, nível de serviço, UF, cidade e status
- 📝 **Observações Persistentes**: Adicione anotações que permanecem ao mudar filtros
- 📥 **Exportação**: Baixe dados filtrados com suas observações em Excel
- 📊 **KPIs em Tempo Real**: Métricas atualizadas automaticamente

---

## 🚀 Como Usar

1. **Faça upload** do arquivo Excel (formato especificado abaixo)
2. **Aplique filtros** conforme necessário
3. **Adicione observações** diretamente nas tabelas
4. **Exporte** os resultados para Excel

---

## 📁 Formato do Arquivo Excel

O arquivo deve conter **duas abas obrigatórias**:

### Aba "coletas"
| Coluna | Descrição |
|--------|-----------|
| CIDADE ORIGEM | Cidade de origem |
| CIDADE DESTINO | Cidade de destino |
| DTM | Número DTM |
| EMPRESA ORIGEM | Empresa de origem |
| OS | Ordem de Serviço |
| DATA COLETA | Data da coleta |
| NÍVEL DE SERVIÇO | Tipo de serviço |
| UF ORIGEM | UF de origem |

### Aba "entregas"
| Coluna | Descrição |
|--------|-----------|
| CIDADE ORIGEM | Cidade de origem |
| UF ORIGEM | UF de origem |
| CIDADE DESTINO | Cidade de destino |
| UF DESTINO | UF de destino |
| DTM | Número DTM |
| NÍVEL DE SERVIÇO | Tipo de serviço |
| EMPRESA DESTINO | Empresa de destino |
| PREVISÃO DE ENTREGA | Data prevista |
| DATA DE ENTREGA | Data efetiva |
| EMBARQUE | Número de embarque |
| CTE | Número CTE |

---

## 💻 Instalação Local

```bash
# Clone o repositório
git clone https://github.com/SEU-USUARIO/REPO-NOME.git
cd REPO-NOME

# Instale as dependências
pip install -r requirements.txt

# Execute o dashboard
streamlit run app.py
```

Acesse: `http://localhost:8501`

---

## 🔧 Tecnologias

- **Python 3.8+**
- **Streamlit** - Framework web
- **Pandas** - Manipulação de dados
- **OpenPyxl** - Leitura de Excel

---

## 📝 Observações Importantes

⚠️ **Persistência de Dados**: As observações são armazenadas na sessão do navegador. Para salvar permanentemente, use o botão de exportação.

⚠️ **Formato do Excel**: Mantenha sempre o mesmo layout e nomes de colunas para evitar erros.

---

## 📄 Licença

Projeto desenvolvido para uso interno PETROBRAS.
