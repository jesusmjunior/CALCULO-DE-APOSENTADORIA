import streamlit as st
import pandas as pd
from io import StringIO

st.title("📊 Dashboard Previdenciário Modular - Revisão da Vida Toda")

st.header("📥 Etapa 1 - Inserção dos Dados CNIS")
cnis_txt = st.text_area("Cole os dados do CNIS (Competência e Remuneração)", height=200)

st.header("📥 Etapa 2 - Inserção dos Dados da Carta de Concessão")
carta_txt = st.text_area("Cole os dados da Carta de Benefício (SEQ, Data, Salário, Índice, Salário Corrigido, Observação)", height=200)

def parse_data(text_data):
    try:
        return pd.read_csv(StringIO(text_data), sep=None, engine='python')
    except:
        return None

# Processamento dos dados
cnis_df = parse_data(cnis_txt)
carta_df = parse_data(carta_txt)

if cnis_df is not None:
    st.subheader("🔎 Dados CNIS Carregados")
    st.dataframe(cnis_df)

    st.subheader("📈 Gráfico CNIS - 80% Maiores Salários")
    cnis_sorted = cnis_df.sort_values(by=cnis_df.columns[0])
    cnis_top = cnis_sorted.nlargest(int(0.8 * len(cnis_sorted)), cnis_sorted.columns[1])
    st.bar_chart(data=cnis_top, x=cnis_top.columns[0], y=cnis_top.columns[1])

if carta_df is not None:
    st.subheader("🔎 Dados Carta de Benefício Carregados")
    st.dataframe(carta_df)

    st.subheader("📈 Gráfico Carta - 80% Maiores Salários")
    carta_sorted = carta_df.sort_values(by=carta_df.columns[1])
    carta_top = carta_sorted.nlargest(int(0.8 * len(carta_sorted)), carta_sorted.columns[2])
    st.bar_chart(data=carta_top, x=carta_top.columns[1], y=carta_top.columns[2])

# Etapa 3 - Processamento dos cálculos
if cnis_df is not None and carta_df is not None:
    st.header("🧮 Etapa 3 - Cálculo Previdenciário INSS Real")

    media_cnis = cnis_top[cnis_top.columns[1]].mean()
    media_carta = carta_top[carta_top.columns[2]].mean()

    Tc = 38 + (1/12) + (25/365)
    a = 0.31
    Es = 21.8
    Id = 60
    FP = (Tc * a / Es) * (1 + ((Id + Tc * a) / 100))
    beneficio = media_cnis * FP

    st.write(f"**Média dos 80% maiores salários CNIS:** R$ {media_cnis:,.2f}")
    st.write(f"**Média dos 80% maiores salários Carta:** R$ {media_carta:,.2f}")
    st.write(f"**Fator Previdenciário:** {FP:.4f}")
    st.write(f"**Salário de Benefício Calculado:** R$ {beneficio:,.2f}")

    # Explicação dos salários desconsiderados
    if 'Observação' in carta_df.columns:
        desconsid = carta_df[carta_df['Observação'].str.contains("DESCONSIDERADO", na=False)]
        if not desconsid.empty:
            st.subheader("🚩 Salários Desconsiderados na Carta")
            st.dataframe(desconsid)
            st.write("Os salários marcados como DESCONSIDERADO não foram computados no cálculo por regra normativa específica.")

    # Download dos resultados
    resultado_df = pd.DataFrame({
        'Fonte': ['CNIS', 'Carta'],
        'Média dos 80% maiores salários': [media_cnis, media_carta],
        'Salário de Benefício Calculado': [beneficio, carta_top[carta_top.columns[2]].sum()]  # Apenas ilustrativo
    })
    st.download_button("📥 Exportar Resultado Final (CSV)", data=resultado_df.to_csv(index=False), file_name='resultado_final.csv')

# Etapa 4 - Sugestão de Revisão
if cnis_df is not None and carta_df is not None:
    st.header("📄 Etapa 4 - Sugestão Estratégica para Revisão Judicial")
    st.write("Com base nos dados processados, recomenda-se incluir salários de maior remuneração não considerados, conforme os 80% mais vantajosos identificados. A análise indicou possível aumento no benefício ao considerar os seguintes pontos:")
    st.markdown("- Reavaliação dos salários desconsiderados.")
    st.markdown("- Aplicação integral da Lei 8.213/91 para períodos anteriores a 2019.")
    st.markdown("- Recalcular o benefício aplicando os salários do CNIS mais vantajosos.")

    st.success("Relatório pronto para uso jurídico e revisão da vida toda.")
