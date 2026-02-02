import streamlit as st
import pandas as pd

# =========================
# CONFIGURAÇÃO DA PÁGINA
# =========================
st.set_page_config(
    page_title="RDA THS - PETROBRAS | Dashboard Diário",
    page_icon="📊",
    layout="wide",
)

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1400px; }
      [data-testid="stMetricValue"] { font-size: 1.6rem; }
      .small-note { opacity: 0.78; font-size: 0.9rem; margin-top: -0.4rem; }
      .section-title { font-weight: 800; font-size: 1.05rem; margin: 0.25rem 0 0.75rem; }
      .pill { display:inline-block; padding:0.15rem 0.55rem; border-radius:999px; font-size:0.85rem; background:#f2f4f7; }
      .warn { background:#fff3cd; padding:0.5rem 0.75rem; border-radius:10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 RDA THS - PETROBRAS — Dashboard Diário")
st.markdown(
    "<div class='small-note'>Faça upload diário do Excel no mesmo formato (abas: <b>coletas</b> e <b>entregas</b>). O dashboard atualiza automaticamente.</div>",
    unsafe_allow_html=True
)

# =========================
# FUNÇÕES AUXILIARES
# =========================
REQUIRED_SHEETS = ["coletas", "entregas"]

def norm_key(s: str) -> str:
    """Normaliza chave para comparação (minúsculo + remove acentos básicos + espaços extras)."""
    if s is None:
        return ""
    s = str(s).strip().lower()
    # remoção simples de acentos comuns pt-BR
    repl = str.maketrans({
        "á":"a","à":"a","â":"a","ã":"a",
        "é":"e","ê":"e",
        "í":"i",
        "ó":"o","ô":"o","õ":"o",
        "ú":"u",
        "ç":"c",
        "°":"o",
    })
    s = s.translate(repl)
    s = " ".join(s.split())
    return s

def pick_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Retorna o nome real da coluna no DF que corresponde a uma das opções (com normalização)."""
    if df is None or df.empty:
        return None
    cols = list(df.columns)
    norm_map = {norm_key(c): c for c in cols}

    for c in candidates:
        key = norm_key(c)
        if key in norm_map:
            return norm_map[key]
    return None

def ensure_cols(df: pd.DataFrame, mapping: dict[str, list[str]], context: str) -> dict[str, str]:
    """
    mapping: {col_canonica: [candidatos possíveis]}
    retorna {col_canonica: nome_real_no_df}
    """
    resolved = {}
    missing = []
    for canon, cands in mapping.items():
        real = pick_col(df, cands)
        if real is None:
            missing.append(canon)
        else:
            resolved[canon] = real
    if missing:
        st.error(
            f"❌ Faltam colunas obrigatórias em **{context}**: {', '.join(missing)}.\n\n"
            "Verifique se o arquivo do dia mantém o mesmo layout e nomes."
        )
        st.stop()
    return resolved

def read_excel(uploaded_file) -> tuple[pd.DataFrame, pd.DataFrame]:
    xls = pd.ExcelFile(uploaded_file)
    sheet_names = xls.sheet_names
    sheet_map = {norm_key(n): n for n in sheet_names}

    missing = [s for s in REQUIRED_SHEETS if norm_key(s) not in sheet_map]
    if missing:
        st.error(f"❌ Abas obrigatórias ausentes: {missing}. Esperado: {REQUIRED_SHEETS}")
        st.stop()

    coletas = pd.read_excel(uploaded_file, sheet_name=sheet_map["coletas"])
    entregas = pd.read_excel(uploaded_file, sheet_name=sheet_map["entregas"])
    return coletas, entregas

def to_dt(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")

def safe_str(series: pd.Series) -> pd.Series:
    return series.astype("string")

def date_filter_ui(label: str, dt_series: pd.Series):
    """Retorna (start_date, end_date, include_missing)."""
    dt_series = pd.to_datetime(dt_series, errors="coerce")
    valid = dt_series.dropna()

    col1, col2, col3 = st.columns([2, 2, 2])
    if valid.empty:
        with col1:
            st.info(f"{label}: não há datas preenchidas (tudo vazio).")
        with col2:
            start = None
            end = None
        with col3:
            include_missing = st.checkbox("Incluir registros sem data", value=True, key=f"{label}_missing")
        return start, end, include_missing

    min_d = valid.min().date()
    max_d = valid.max().date()

    with col1:
        start = st.date_input(f"{label} (início)", value=min_d, min_value=min_d, max_value=max_d, key=f"{label}_start")
    with col2:
        end = st.date_input(f"{label} (fim)", value=max_d, min_value=min_d, max_value=max_d, key=f"{label}_end")
    with col3:
        include_missing = st.checkbox("Incluir registros sem data", value=True, key=f"{label}_missing")

    return start, end, include_missing

def apply_date_filter(df: pd.DataFrame, dt_col: str, start, end, include_missing: bool):
    if start is None or end is None:
        return df if include_missing else df[df[dt_col].notna()]

    mask = df[dt_col].between(pd.Timestamp(start), pd.Timestamp(end), inclusive="both")
    if include_missing:
        mask = mask | df[dt_col].isna()
    return df[mask]

# =========================
# UPLOAD DO ARQUIVO
# =========================
uploaded = st.file_uploader("📤 Envie o Excel do dia (mesmo layout)", type=["xlsx"])

if not uploaded:
    st.info("Envie o arquivo Excel para iniciar.")
    st.stop()

# Verifica se é um novo arquivo (inicializa/reseta session state)
if "uploaded_file_name" not in st.session_state or st.session_state["uploaded_file_name"] != uploaded.name:
    st.session_state["uploaded_file_name"] = uploaded.name
    st.session_state["master_coletas"] = None
    st.session_state["master_entregas"] = None

raw_coletas, raw_entregas = read_excel(uploaded)

# =========================
# MAPEAMENTO DE COLUNAS
# =========================
COLETAS_COLS = ensure_cols(
    raw_coletas,
    {
        "CIDADE_ORIGEM": ["CIDADE ORIGEM"],
        "CIDADE_DESTINO": ["CIDADE DESTINO"],
        "DTM": ["DTM"],
        "EMPRESA_ORIGEM": ["EMPRESA ORIGEM"],
        "OS": ["OS"],
        "DATA_COLETA": ["DATA COLETA", "DATA DE COLETA"],
        "NIVEL_SERVICO": ["NIVEL DE SERVIÇO", "NÍVEL DE SERVIÇO", "NIVEL DE SERVICO", "NIVEL SERVICO"],
        "UF_ORIGEM": ["UF ORIGEM"],
    },
    context="COLETAS"
)

ENTREGAS_COLS = ensure_cols(
    raw_entregas,
    {
        "CIDADE_ORIGEM": ["CIDADE ORIGEM"],
        "UF_ORIGEM": ["UF ORIGEM"],
        "CIDADE_DESTINO": ["CIDADE DESTINO"],
        "UF_DESTINO": ["UF DESTINO"],
        "DTM": ["DTM"],
        "NIVEL_SERVICO": ["NIVEL DE SERVIÇO", "NÍVEL DE SERVIÇO", "NIVEL DE SERVICO", "NIVEL SERVICO"],
        "EMPRESA_DESTINO": ["EMPRESA DESTINO"],
        "PREV_ENTREGA": ["PREVISÃO DE ENTREGA", "PREVISAO DE ENTREGA", "PREVISAO ENTREGA", "PREVISÃO ENTREGA"],
        "DATA_ENTREGA": ["DATA DE ENTREGA", "DATA ENTREGA"],
        "EMBARQUE": ["EMBARQUE"],
        "CTE": ["CTE"],
    },
    context="ENTREGAS"
)

# =========================
# NORMALIZAÇÃO DOS DADOS
# =========================
def normalize_coletas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    dt = to_dt(df[COLETAS_COLS["DATA_COLETA"]])
    df["_DATA_COLETA_DT"] = dt

    exib = dt.dt.strftime("%Y-%m-%d")
    exib = exib.where(~dt.isna(), "Material não coletado")
    df["DATA DE COLETA"] = exib

    os_ = safe_str(df[COLETAS_COLS["OS"]])
    os_ = os_.where(~(os_.isna() | (os_.str.strip() == "")), "Sem número de OS")
    df["OS"] = os_

    out = pd.DataFrame({
        "CIDADE ORIGEM": df[COLETAS_COLS["CIDADE_ORIGEM"]],
        "CIDADE DESTINO": df[COLETAS_COLS["CIDADE_DESTINO"]],
        "DTM": df[COLETAS_COLS["DTM"]],
        "EMPRESA ORIGEM": df[COLETAS_COLS["EMPRESA_ORIGEM"]],
        "OS": df["OS"],
        "DATA DE COLETA": df["DATA DE COLETA"],
        "NÍVEL DE SERVIÇO": df[COLETAS_COLS["NIVEL_SERVICO"]],
        "UF ORIGEM": df[COLETAS_COLS["UF_ORIGEM"]],
        "_DATA_COLETA_DT": df["_DATA_COLETA_DT"],
    })

    return out

def normalize_entregas(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    prev = to_dt(df[ENTREGAS_COLS["PREV_ENTREGA"]])
    df["_PREV_ENTREGA_DT"] = prev

    dt_ent = to_dt(df[ENTREGAS_COLS["DATA_ENTREGA"]])
    df["_DATA_ENTREGA_DT"] = dt_ent
    
    exib_ent = dt_ent.dt.strftime("%Y-%m-%d")
    exib_ent = exib_ent.where(~dt_ent.isna(), "Não entregue")
    df["DATA DE ENTREGA_EXIB"] = exib_ent

    origem_destino = (
        safe_str(df[ENTREGAS_COLS["CIDADE_ORIGEM"]]).fillna("") + " / " +
        safe_str(df[ENTREGAS_COLS["UF_ORIGEM"]]).fillna("") + "  →  " +
        safe_str(df[ENTREGAS_COLS["CIDADE_DESTINO"]]).fillna("") + " / " +
        safe_str(df[ENTREGAS_COLS["UF_DESTINO"]]).fillna("")
    ).str.replace(r"\s+", " ", regex=True).str.strip()

    out = pd.DataFrame({
        "ORIGEM → DESTINO": origem_destino,
        "DTM": df[ENTREGAS_COLS["DTM"]],
        "NÍVEL DE SERVIÇO": df[ENTREGAS_COLS["NIVEL_SERVICO"]],
        "EMPRESA DESTINO": df[ENTREGAS_COLS["EMPRESA_DESTINO"]],
        "DATA DE ENTREGA": df["DATA DE ENTREGA_EXIB"],
        "EMBARQUE": df[ENTREGAS_COLS["EMBARQUE"]],
        "CTE": df[ENTREGAS_COLS["CTE"]],
        "UF DESTINO": df[ENTREGAS_COLS["UF_DESTINO"]],
        "CIDADE DESTINO": df[ENTREGAS_COLS["CIDADE_DESTINO"]],
        "_PREV_ENTREGA_DT": df["_PREV_ENTREGA_DT"],
        "_DATA_ENTREGA_DT": df["_DATA_ENTREGA_DT"],
    })

    return out

coletas = normalize_coletas(raw_coletas)
entregas = normalize_entregas(raw_entregas)

# Inicializa master dataframes com IDs únicos e coluna de observações
if st.session_state["master_coletas"] is None:
    coletas["_ID"] = range(len(coletas))
    coletas["OBSERVAÇÕES"] = ""
    st.session_state["master_coletas"] = coletas.copy()
else:
    coletas = st.session_state["master_coletas"].copy()

if st.session_state["master_entregas"] is None:
    entregas["_ID"] = range(len(entregas))
    entregas["OBSERVAÇÕES"] = ""
    st.session_state["master_entregas"] = entregas.copy()
else:
    entregas = st.session_state["master_entregas"].copy()

# =========================
# RESUMO DO ARQUIVO
# =========================
with st.expander("📌 Resumo do arquivo carregado", expanded=False):
    c1, c2, c3 = st.columns(3)
    c1.metric("Linhas (Coletas)", len(coletas))
    c2.metric("Linhas (Entregas)", len(entregas))
    c3.metric("DTMs únicas (total)", pd.concat([coletas["DTM"], entregas["DTM"]]).nunique(dropna=True))

# =========================
# CALLBACKS PARA ATUALIZAR OBSERVAÇÕES
# =========================
def update_coletas():
    """Atualiza as observações no master dataframe de coletas."""
    if "editor_coletas" in st.session_state:
        edited_data = st.session_state["editor_coletas"]
        if "edited_rows" in edited_data and edited_data["edited_rows"]:
            # Verifica se temos a visualização anterior
            if "view_coletas" in st.session_state:
                view_df = st.session_state["view_coletas"]
                master = st.session_state["master_coletas"]
                
                # Atualiza cada linha editada
                for row_idx, changes in edited_data["edited_rows"].items():
                    if "OBSERVAÇÕES" in changes and row_idx < len(view_df):
                        # Pega o ID original da linha
                        original_id = view_df.iloc[row_idx]["_ID"]
                        # Atualiza no master dataframe
                        master.loc[master["_ID"] == original_id, "OBSERVAÇÕES"] = changes["OBSERVAÇÕES"]

def update_entregas():
    """Atualiza as observações no master dataframe de entregas."""
    if "editor_entregas" in st.session_state:
        edited_data = st.session_state["editor_entregas"]
        if "edited_rows" in edited_data and edited_data["edited_rows"]:
            # Verifica se temos a visualização anterior
            if "view_entregas" in st.session_state:
                view_df = st.session_state["view_entregas"]
                master = st.session_state["master_entregas"]
                
                # Atualiza cada linha editada
                for row_idx, changes in edited_data["edited_rows"].items():
                    if "OBSERVAÇÕES" in changes and row_idx < len(view_df):
                        # Pega o ID original da linha
                        original_id = view_df.iloc[row_idx]["_ID"]
                        # Atualiza no master dataframe
                        master.loc[master["_ID"] == original_id, "OBSERVAÇÕES"] = changes["OBSERVAÇÕES"]

tabs = st.tabs(["🚚 Coletas", "📦 Entregas"])

# =========================
# ABA COLETAS
# =========================
with tabs[0]:
    st.markdown("<div class='section-title'>Filtros — Coletas</div>", unsafe_allow_html=True)

    # 1) DATA COLETA
    start, end, include_missing = date_filter_ui("DATA COLETA", coletas["_DATA_COLETA_DT"])
    tmp = apply_date_filter(coletas, "_DATA_COLETA_DT", start, end, include_missing)

    # 2) NÍVEL DE SERVIÇO
    ns_opts = sorted([x for x in tmp["NÍVEL DE SERVIÇO"].dropna().unique()])
    ns_sel = st.multiselect("NÍVEL DE SERVIÇO", options=ns_opts, default=ns_opts, key="coletas_ns")
    if ns_sel:
        tmp = tmp[tmp["NÍVEL DE SERVIÇO"].isin(ns_sel)]

    # 3) UF ORIGEM
    uf_opts = sorted([x for x in tmp["UF ORIGEM"].dropna().unique()])
    uf_sel = st.selectbox("UF ORIGEM", options=["(Todas)"] + uf_opts, key="coletas_uf")
    if uf_sel != "(Todas)":
        tmp = tmp[tmp["UF ORIGEM"] == uf_sel]

    # 4) CIDADE ORIGEM (dependente da UF)
    cid_opts = sorted([x for x in tmp["CIDADE ORIGEM"].dropna().unique()])
    if uf_sel == "(Todas)":
        st.caption("Selecione a UF ORIGEM para refinar por CIDADE ORIGEM (opcional).")
    cid_sel = st.selectbox("CIDADE ORIGEM (após UF)", options=["(Todas)"] + cid_opts, key="coletas_cidade")
    if cid_sel != "(Todas)":
        tmp = tmp[tmp["CIDADE ORIGEM"] == cid_sel]

    # 5) OS (status) - NOVO FILTRO
    os_status = st.selectbox(
        "OS (status)", 
        options=["(Todas)", "Sem número de OS", "Com número de OS"],
        key="coletas_os_status"
    )
    if os_status == "Sem número de OS":
        tmp = tmp[tmp["OS"] == "Sem número de OS"]
    elif os_status == "Com número de OS":
        tmp = tmp[tmp["OS"] != "Sem número de OS"]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Registros", len(tmp))
    k2.metric("DTMs únicas", tmp["DTM"].nunique(dropna=True))
    k3.metric("Sem OS", int((tmp["OS"] == "Sem número de OS").sum()))
    k4.metric("Material não coletado", int((tmp["DATA DE COLETA"] == "Material não coletado").sum()))

    # Tabela final (somente campos solicitados) com coluna editável
    view_cols = ["CIDADE ORIGEM", "CIDADE DESTINO", "DTM", "EMPRESA ORIGEM", "OS", "DATA DE COLETA"]
    display_df = tmp[view_cols + ["_ID", "OBSERVAÇÕES"]].copy().reset_index(drop=True)
    
    # Salva a visualização atual para o callback
    st.session_state["view_coletas"] = display_df.copy()
    
    # Prepara DataFrame para exibição (remove _ID)
    display_for_editor = display_df.drop(columns=["_ID"])
    
    # Editor de dados interativo com callback
    edited_coletas = st.data_editor(
        display_for_editor,
        use_container_width=True,
        height=560,
        disabled=view_cols,  # Apenas OBSERVAÇÕES pode ser editada
        key="editor_coletas",
        on_change=update_coletas
    )
    
    # Botão de download
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_coletas.to_excel(writer, sheet_name='Coletas', index=False)
    
    st.download_button(
        label="📥 Exportar Coletas (Excel)",
        data=output.getvalue(),
        file_name=f"coletas_exportadas_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_coletas"
    )

# =========================
# ABA ENTREGAS
# =========================
with tabs[1]:
    st.markdown("<div class='section-title'>Filtros — Entregas</div>", unsafe_allow_html=True)

    # 1) PREVISÃO DE ENTREGA
    start, end, include_missing = date_filter_ui("PREVISÃO DE ENTREGA", entregas["_PREV_ENTREGA_DT"])
    tmp = apply_date_filter(entregas, "_PREV_ENTREGA_DT", start, end, include_missing)

    # 2) NÍVEL DE SERVIÇO - NOVO FILTRO
    ns_opts = sorted([x for x in tmp["NÍVEL DE SERVIÇO"].dropna().unique()])
    ns_sel = st.multiselect("NÍVEL DE SERVIÇO", options=ns_opts, default=ns_opts, key="entregas_ns")
    if ns_sel:
        tmp = tmp[tmp["NÍVEL DE SERVIÇO"].isin(ns_sel)]

    # 3) UF DESTINO
    uf_opts = sorted([x for x in tmp["UF DESTINO"].dropna().unique()])
    uf_sel = st.selectbox("UF DESTINO", options=["(Todas)"] + uf_opts, key="entregas_uf")
    if uf_sel != "(Todas)":
        tmp = tmp[tmp["UF DESTINO"] == uf_sel]

    # 4) CIDADE DESTINO (dependente da UF)
    cid_opts = sorted([x for x in tmp["CIDADE DESTINO"].dropna().unique()])
    if uf_sel == "(Todas)":
        st.caption("Selecione a UF DESTINO para refinar por CIDADE DESTINO (opcional).")
    cid_sel = st.selectbox("CIDADE DESTINO (após UF)", options=["(Todas)"] + cid_opts, key="entregas_cidade")
    if cid_sel != "(Todas)":
        tmp = tmp[tmp["CIDADE DESTINO"] == cid_sel]

    # 5) DATA DE ENTREGA (status) - NOVO FILTRO
    ent_status = st.selectbox(
        "DATA DE ENTREGA (status)", 
        options=["(Todas)", "Não entregue", "Entregue"],
        key="entregas_ent_status"
    )
    if ent_status == "Não entregue":
        tmp = tmp[tmp["DATA DE ENTREGA"] == "Não entregue"]
    elif ent_status == "Entregue":
        tmp = tmp[tmp["DATA DE ENTREGA"] != "Não entregue"]

    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Registros", len(tmp))
    k2.metric("DTMs únicas", tmp["DTM"].nunique(dropna=True))
    k3.metric("Não entregue", int((tmp["DATA DE ENTREGA"] == "Não entregue").sum()))
    k4.metric("Níveis de serviço", tmp["NÍVEL DE SERVIÇO"].nunique(dropna=True))

    # Tabela final (somente campos solicitados) com coluna editável
    view_cols = ["ORIGEM → DESTINO", "DTM", "NÍVEL DE SERVIÇO", "EMPRESA DESTINO", "DATA DE ENTREGA", "EMBARQUE", "CTE"]
    display_df = tmp[view_cols + ["_ID", "OBSERVAÇÕES"]].copy().reset_index(drop=True)
    
    # Salva a visualização atual para o callback
    st.session_state["view_entregas"] = display_df.copy()
    
    # Prepara DataFrame para exibição (remove _ID)
    display_for_editor = display_df.drop(columns=["_ID"])
    
    # Editor de dados interativo com callback
    edited_entregas = st.data_editor(
        display_for_editor,
        use_container_width=True,
        height=560,
        disabled=view_cols,  # Apenas OBSERVAÇÕES pode ser editada
        key="editor_entregas",
        on_change=update_entregas
    )
    
    # Botão de download
    import io
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        edited_entregas.to_excel(writer, sheet_name='Entregas', index=False)
    
    st.download_button(
        label="📥 Exportar Entregas (Excel)",
        data=output.getvalue(),
        file_name=f"entregas_exportadas_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key="download_entregas"
    )
