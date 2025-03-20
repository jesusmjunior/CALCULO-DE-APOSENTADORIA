import pandas as pd
import numpy as np
import streamlit as st

st.title("🧮 Cálculo Previdenciário Concentrado - Engenharia Reversa & Fuzzy")

st.header("📥 Carregar Dados Pré-Processados (CNIS e Carta)")

uploaded_cnis = st.file_uploader("Importe o arquivo CSV dos 80% maiores salários CNIS", type="csv")
uploaded_carta = st.file_uploader("Importe o arquivo CSV dos 80% maiores salários da Carta de Benefício", type="csv")

# ============== Função para Cálculo Fuzzy Previdenciário Modular ===================
def fator_previdenciario(Tc, a, Es, Id):
    return round((Tc * a / Es) * (1 + ((Id + Tc * a) / 100)), 4)

def salario_beneficio(media_salarios, FP):
    return round(media_salarios * FP, 2)

def renda_mensal_inicial(salario_beneficio, coef=1.0):
    return round(salario_beneficio * coef, 2)

# =========================
# 🚀 Cálculo Real e Engenharia Reversa
# =========================
if uploaded_cnis and uploaded_carta:
    cnis_df = pd.read_csv(uploaded_cnis)
    carta_df = pd.read_csv(uploaded_carta)

    st.subheader("📊 Dados CNIS Importados")
    st.dataframe(cnis_df)
    st.subheader("📊 Dados Carta Importados")
    st.dataframe(carta_df)

    media_cnis = cnis_df[cnis_df.columns[1]].mean()
    media_carta = carta_df[carta_df.columns[2]].mean()

    # Parâmetros Fixos
    Tc = 38 + (1/12) + (25/365)  # Tempo contribuição: 38 anos, 1 mês, 25 dias
    a = 0.31
    Es = 21.8
    Id = 60
    coef = 1.0

    FP = fator_previdenciario(Tc, a, Es, Id)
    salario_benef = salario_beneficio(media_cnis, FP)
    renda_inicial = renda_mensal_inicial(salario_benef, coef)

    st.header("📑 Resultado do Cálculo Previdenciário Real")
    st.write(f"**Média dos 80% maiores salários CNIS:** R$ {media_cnis:,.2f}")
    st.write(f"**Fator Previdenciário Calculado:** {FP}")
    st.write(f"**Salário de Benefício Calculado:** R$ {salario_benef:,.2f}")
    st.write(f"**Renda Mensal Inicial Calculada:** R$ {renda_inicial:,.2f}")

    # ===================
    # 🔍 Identificação de Salários Críticos
    # ===================
    st.subheader("🚩 Salários Críticos Identificados")

    desconsid = carta_df[carta_df.columns].apply(lambda x: x.astype(str).str.contains("DESCONSIDERADO", na=False)).any(axis=1)
    criticos = carta_df[desconsid]

    if not criticos.empty:
        st.dataframe(criticos)
        st.warning("Existem salários desconsiderados que podem impactar negativamente o cálculo do benefício. Recomenda-se revisão!")
    else:
        st.success("Nenhum salário desconsiderado identificado na carta.")

    # Exportação dos Resultados
    resultado_df = pd.DataFrame({
        'Fonte': ['CNIS'],
        'Média dos 80% maiores salários': [media_cnis],
        'Fator Previdenciário': [FP],
        'Salário de Benefício Calculado': [salario_benef],
        'Renda Mensal Inicial': [renda_inicial]
    })

    st.download_button("📥 Exportar Resultado do Cálculo (CSV)", data=resultado_df.to_csv(index=False), file_name='resultado_calculo_inss.csv')

    # Engenharia reversa explicada
    st.header("📚 Engenharia Reversa do Cálculo Aplicada")
    st.markdown("""
    - **Tempo de Contribuição (Tc):** 38 anos, 1 mês, 25 dias
    - **Expectativa de Sobrevida (Es):** 21,8 anos (IBGE)
    - **Idade do Segurado (Id):** 60 anos
    - **Alíquota Previdenciária (a):** 31%
    - **Coeficiente:** 100%
    
    **Fórmula:**
    
    \[
    FP = \left(\frac{T_c \times a}{E_s}\right) \times \left(1 + \frac{(I_d + T_c \times a)}{100}\right)
    \]
    
    Aplicado diretamente nos dados importados, sem alteração ou interpolação, respeitando os parâmetros legais.
    """)
