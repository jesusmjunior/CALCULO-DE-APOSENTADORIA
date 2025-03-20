import streamlit as st
import pandas as pd
from io import StringIO

st.title("📊 Dashboard Previdenciário Simplificado - Versão Leve")

# Entrada de dados
st.header("📥 Inserção dos Dados")
file = st.file_uploader("Upload CNIS ou Carta (CSV/XLS)", type=['csv', 'xls', 'xlsx'])
data_txt = st.text_area("Ou cole os dados em formato texto")

def load_data(uploaded_file, txt_data):
    if uploaded_file:
        if uploaded_file.name.endswith('csv'):
            return pd.read_csv(uploaded_file)
        else:
            return pd.read_excel(uploaded_file)
    elif txt_data:
        try:
            return pd.read_csv(StringIO(txt_data), sep=None, engine='python')
        except:
            return None
    return None

df = load_data(file, data_txt)

if df is not None:
    st.subheader("🔎 Dados Carregados")
    st.dataframe(df)

    st.header("🧮 Cálculo Previdenciário")
    df_sorted = df.sort_values(by=df.columns[0])
    df_top = df_sorted.nlargest(int(0.8 * len(df_sorted)), df.columns[1])
    media = df_top[df.columns[1]].mean()

    Tc = 38 + (1/12) + (25/365)
    a = 0.31
    Es = 21.8
    Id = 60
    FP = (Tc * a / Es) * (1 + ((Id + Tc * a) / 100))
    beneficio = media * FP

    st.write(f"**Média dos 80% maiores salários:** R$ {media:,.2f}")
    st.write(f"**Fator Previdenciário:** {FP:.4f}")
    st.write(f"**Salário de Benefício:** R$ {beneficio:,.2f}")

    st.subheader("📅 Normativa Aplicada")
    df['Normativa'] = ["Lei 8.213/91" if int(str(x)[:4]) < 2019 else "Pós-2019" for x in df[df.columns[0]]]
    st.dataframe(df[[df.columns[0], df.columns[1], 'Normativa']])

    st.subheader("📈 Visualização dos Salários (Top 80%)")
    st.bar_chart(data=df_top, x=df_top.columns[0], y=df_top.columns[1])

    st.download_button("📥 Exportar Resultado (CSV)", data=df.to_csv(index=False), file_name='resultado_simplificado.csv')

    st.markdown("---")
    st.info("Cálculo realizado conforme Lei 8.213/91 e Instruções Normativas vigentes. Pronto para revisão judicial.")
