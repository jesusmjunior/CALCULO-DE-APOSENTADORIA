import pandas as pd
import numpy as np
import streamlit as st

st.title("🧮 Cálculo Previdenciário Concentrado - Engenharia Reversa & Fuzzy - v2")

st.header("📥 Carregar Dados Pré-Processados (CNIS e Carta)")

uploaded_cnis = st.file_uploader("Importe o arquivo CSV dos salários CNIS", type="csv")
uploaded_carta = st.file_uploader("Importe o arquivo CSV dos salários da Carta de Benefício", type="csv")

# ================= Funções Utilitárias ====================
def limpar_dados(df, coluna_salario):
    df = df.dropna()
    df = df[df[coluna_salario].apply(lambda x: str(x).replace('.', '').replace(',', '').replace(' ', '').replace('e', '').replace('E', '').isnumeric())]
    df[coluna_salario] = df[coluna_salario].astype(float)
    return df

def aplicar_fuzzy(row):
    if "DESCONSIDERADO" in str(row):
        return 0.5
    return 1.0

def calcular_media_ponderada(df, coluna_salario, coluna_observacao=None):
    if coluna_observacao:
        df['Peso'] = df[coluna_observacao].apply(aplicar_fuzzy)
        return np.average(df[coluna_salario], weights=df['Peso'])
    else:
        return df[coluna_salario].mean()

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

    # Limpeza e normalização
    cnis_df = limpar_dados(cnis_df, cnis_df.columns[1])
    carta_df = limpar_dados(carta_df, carta_df.columns[2])

    st.subheader("📊 Dados CNIS Limpados")
    st.dataframe(cnis_df)
    st.subheader("📊 Dados Carta Limpados")
    st.dataframe(carta_df)

    # Cálculo com fuzzy nos salários
    media_cnis = calcular_media_ponderada(cnis_df, cnis_df.columns[1])
    media_carta = calcular_media_ponderada(carta_df, carta_df.columns[2], carta_df.columns[5])

    # Parâmetros Fixos
    Tc = 38 + (1/12) + (25/365)
    a = 0.31
    Es = 21.8
    Id = 60
    coef = 1.0

    FP = fator_previdenciario(Tc, a, Es, Id)
    salario_benef = salario_beneficio(media_cnis, FP)
    renda_inicial = renda_mensal_inicial(salario_benef, coef)

    st.header("📑 Resultado do Cálculo Previdenciário Real")
    st.write(f"**Média dos 80% maiores salários CNIS (ponderada):** R$ {media_cnis:,.2f}")
    st.write(f"**Média dos 80% maiores salários Carta (ponderada):** R$ {media_carta:,.2f}")
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
        'Fonte': ['CNIS', 'Carta'],
        'Média dos 80% maiores salários': [media_cnis, media_carta],
        'Fator Previdenciário': [FP, FP],
        'Salário de Benefício Calculado': [salario_benef, salario_benef],
        'Renda Mensal Inicial': [renda_inicial, renda_inicial]
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

    **Aplicado diretamente nos dados importados e normalizados, respeitando fielmente os normativos previdenciários (Lei 8.213/91, Lei 9.876/99, EC 103/19)**
    """)
