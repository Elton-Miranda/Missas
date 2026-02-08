# app.py
import streamlit as st
import pandas as pd
from datetime import datetime
import locale
from dados import MISSAS # Importa a lista do outro arquivo

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="Missas Diocese SJC", page_icon="⛪", layout="centered")

# --- CARREGAMENTO DE DADOS ---
@st.cache_data
def carregar_dataframe():
    return pd.DataFrame(MISSAS)

df = carregar_dataframe()

# --- LÓGICA DE TEMPO ---
try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
except:
    pass 

agora = datetime.now()
dia_hoje_int = agora.weekday()
hora_atual = agora.time()
dias_map = {0: "Segunda-feira", 1: "Terça-feira", 2: "Quarta-feira", 3: "Quinta-feira", 4: "Sexta-feira", 5: "Sábado", 6: "Domingo"}
dia_hoje_str = dias_map[dia_hoje_int]

# --- INTERFACE ---
st.title("⛪ Diocese de São José dos Campos")
st.markdown("---")

tab1, tab2 = st.tabs(["🕒 Acontecendo Hoje", "📅 Pesquisa Completa"])

# --- ABA 1: HOJE ---
with tab1:
    st.header(f"Missas de Hoje ({dia_hoje_str})")
    
    # Filtra apenas o dia de hoje
    df_hoje = df[df['Dia'] == dia_hoje_str].copy()
    
    if not df_hoje.empty:
        # Cria objeto de tempo para comparar
        df_hoje['time_obj'] = pd.to_datetime(df_hoje['Horario'], format='%H:%M').dt.time
        
        # Separa o que vem pela frente e o que já passou
        df_proximas = df_hoje[df_hoje['time_obj'] >= hora_atual].sort_values(by='time_obj')
        df_passadas = df_hoje[df_hoje['time_obj'] < hora_atual].sort_values(by='time_obj')

        if not df_proximas.empty:
            st.success(f"Encontramos **{len(df_proximas)}** horários restantes hoje.")
            
            for _, row in df_proximas.iterrows():
                # Card Simples e Limpo
                with st.container():
                    col1, col2 = st.columns([1, 4])
                    col1.metric("Horário", row['Horario'])
                    with col2:
                        st.subheader(row['Paroquia'])
                        st.text(f"📍 {row['Bairro']}")
                        st.caption(f"{row['Cidade']}")
                    st.divider()
        else:
            st.warning("Não há mais missas para hoje.")

        # Opção de ver o histórico do dia
        if not df_passadas.empty:
            with st.expander("Ver horários que já passaram hoje"):
                st.dataframe(
                    df_passadas[['Horario', 'Paroquia', 'Bairro', 'Cidade']], 
                    hide_index=True, 
                    use_container_width=True
                )
    else:
        st.info("Nenhuma missa cadastrada na base para hoje.")

# --- ABA 2: PESQUISA (FILTROS) ---
with tab2:
    st.header("Pesquisar Horários")
    
    # Filtros em Colunas
    col1, col2 = st.columns(2)
    
    with col1:
        # Filtro de Cidade
        cidades_disponiveis = ["Todas"] + sorted(df['Cidade'].unique().tolist())
        cidade_sel = st.selectbox("Cidade:", cidades_disponiveis)
    
    with col2:
        # Filtro de Dia
        dia_sel = st.selectbox("Dia da Semana:", list(dias_map.values()))

    # Lógica de filtragem
    df_filtrado = df[df['Dia'] == dia_sel]
    
    if cidade_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado['Cidade'] == cidade_sel]

    # Filtro opcional de Paróquia (depende da cidade selecionada)
    if not df_filtrado.empty:
        paroquias_disponiveis = ["Todas"] + sorted(df_filtrado['Paroquia'].unique().tolist())
        paroquia_sel = st.selectbox("Filtrar Paróquia (Opcional):", paroquias_disponiveis)
        
        if paroquia_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado['Paroquia'] == paroquia_sel]
            
        # Exibição Final
        st.markdown("### Resultados")
        if not df_filtrado.empty:
            df_filtrado = df_filtrado.sort_values(by='Horario')
            st.dataframe(
                df_filtrado[['Horario', 'Paroquia', 'Bairro', 'Cidade']], 
                hide_index=True, 
                use_container_width=True
            )
        else:
            st.warning("Nenhum horário encontrado com esses filtros.")
    else:
        st.warning("Não há paróquias cadastradas para esta cidade neste dia.")