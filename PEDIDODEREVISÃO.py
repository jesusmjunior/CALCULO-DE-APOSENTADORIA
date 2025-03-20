import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("\ud83c\udf1f Dashboard - Nova Carta de Concess\u00e3o Previdenci\u00e1ria \ud83d\udcc8")

# Upload CSV
uploaded_file = st.sidebar.file_uploader("Upload CSV Tratado", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Resumo
    st.subheader("\ud83d\udcc3 Resumo Final")
    media = df[df['Status'] == 'Considerado']['Sal\u00e1rio Atualizado (R$)'].mean()
    renda_inicial = media * 0.9373

    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="M\u00e9dia Recalculada dos 80% maiores sal\u00e1rios", value=f"R$ {media:,.2f}")
    with col2:
        st.metric(label="Nova Renda Mensal Inicial", value=f"R$ {renda_inicial:,.2f}")

    # Filtros
    st.sidebar.header("\ud83d\udd04 Filtros")
    plano = st.sidebar.multiselect("Plano Econômico", df['Plano Econômico'].unique())
    status = st.sidebar.multiselect("Status", df['Status'].unique())

    df_filtered = df.copy()
    if plano:
        df_filtered = df_filtered[df_filtered['Plano Econômico'].isin(plano)]
    if status:
        df_filtered = df_filtered[df_filtered['Status'].isin(status)]

    # Tabela
    st.subheader("\ud83d\udcc8 Tabela Completa - Compet\u00eancias e Atualiza\u00e7\u00e3o Monet\u00e1ria")
    st.dataframe(df_filtered, height=500)

    # Gr\u00e1ficos
    st.subheader("\ud83d\udcca Gr\u00e1ficos Comparativos")

    # Evolu\u00e7\u00e3o da m\u00e9dia salarial
    df_plot = df_filtered.sort_values(by='Compet\u00eancia')
    plt.figure(figsize=(12, 5))
    plt.plot(df_plot['Compet\u00eancia'], df_plot['Sal\u00e1rio Atualizado (R$)'], label="Sal\u00e1rio Atualizado")
    plt.xticks(rotation=90)
    plt.title("Evolu\u00e7\u00e3o da M\u00e9dia Salarial")
    plt.legend()
    st.pyplot(plt)

    # Comparativo Considerado vs Inclu\u00eddo
    plt.figure(figsize=(12, 5))
    df_status = df_filtered.groupby('Status')['Sal\u00e1rio Atualizado (R$)'].mean()
    df_status.plot(kind='bar', color=['green', 'blue', 'red'])
    plt.title("Comparativo - M\u00e9dia Salarial por Status")
    st.pyplot(plt)

    # Exporta\u00e7\u00e3o
    st.download_button(
        label="\ud83d\udcc4 Baixar CSV Tratado",
        data=df.to_csv(index=False),
        file_name="Nova_Carta_Concessao_Completa.csv",
        mime="text/csv"
    )
else:
    st.warning("\ud83d\udce2 Por favor, carregue o CSV Tratado para iniciar!")
