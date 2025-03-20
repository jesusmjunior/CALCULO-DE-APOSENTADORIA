import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Cálculo Previdenciário - Revisão", layout="wide")

st.title("📊 INSS Cálculo Previdenciário - Revisão da Vida Toda (v4)")

# ===================
# ETAPA 1 - IMPORTAÇÃO DOS DADOS CNIS E CARTA
# ===================

st.sidebar.header("🔽 Etapa 1: Importação dos Dados")
uploaded_cnis = st.sidebar.file_uploader("Importe CSV do CNIS (Competência e Remuneração)", type="csv")
uploaded_carta = st.sidebar.file_uploader("Importe CSV da Carta de Benefício", type="csv")

if uploaded_cnis and uploaded_carta:
    cnis_df = pd.read_csv(uploaded_cnis)
    carta_df = pd.read_csv(uploaded_carta)

    st.subheader("📄 Dados CNIS")
    st.dataframe(cnis_df)
    st.subheader("📄 Dados Carta de Concessão")
    st.dataframe(carta_df)

    # ===================
    # ETAPA 2 - SANITIZAÇÃO E CLASSIFICAÇÃO TEMPORAL
    # ===================

    st.sidebar.header("🔽 Etapa 2: Sanitização & Classificação")

    def limpar_dados(df, col_remuneracao):
        df = df.dropna(subset=[col_remuneracao])
        df = df[df[col_remuneracao].apply(lambda x: str(x).replace('.', '').replace(',', '').replace(' ', '').replace('e', '').replace('E', '').replace('-', '').isdigit())]
        df[col_remuneracao] = df[col_remuneracao].astype(float)
        return df

    cnis_df = limpar_dados(cnis_df, cnis_df.columns[1])
    carta_df = limpar_dados(carta_df, carta_df.columns[2])

    # ===================
    # ETAPA 3 - CORREÇÃO MONETÁRIA
    # ===================

    st.sidebar.header("🔽 Etapa 3: Correção Monetária")

    def aplicar_indice_corrigido(df, col_salario, col_indice):
        df['Salário Corrigido'] = df[col_salario] * df[col_indice]
        return df

    carta_df = aplicar_indice_corrigido(carta_df, carta_df.columns[2], carta_df.columns[3])

    # ===================
    # ETAPA 4 - SELEÇÃO 80% MAIORES SALÁRIOS
    # ===================

    st.sidebar.header("🔽 Etapa 4: Seleção dos 80% Maiores Salários")

    def selecionar_80_maiores(df, col_corrigido):
        n_maiores = int(0.8 * len(df))
        return df.nlargest(n_maiores, col_corrigido)

    top_cnis = selecionar_80_maiores(cnis_df, cnis_df.columns[1])
    top_carta = selecionar_80_maiores(carta_df, carta_df.columns[4])

    st.subheader("📊 80% Maiores Salários CNIS")
    st.dataframe(top_cnis)

    st.subheader("📊 80% Maiores Salários Carta")
    st.dataframe(top_carta)

    # ===================
    # ETAPA 5 - FUNÇÕES DE CÁLCULO MATEMÁTICO INSS
    # ===================

    st.sidebar.header("🔽 Etapa 5: Aplicação do Cálculo Previdenciário")

    def calcular_media(df, col_corrigido):
        return df[col_corrigido].mean()

    media_cnis = calcular_media(top_cnis, top_cnis.columns[1])
    media_carta = calcular_media(top_carta, top_carta.columns[4])

    # Parâmetros previdenciários normativos
    Tc = 38 + (1/12) + (25/365)  # Tempo contribuição
    a = 0.31  # Alíquota
    Es = 21.8  # Expectativa sobrevida
    Id = 60  # Idade
    coef = 1.0  # Coeficiente

    def fator_previdenciario(Tc, a, Es, Id):
        return round((Tc * a / Es) * (1 + ((Id + Tc * a) / 100)), 4)

    FP = fator_previdenciario(Tc, a, Es, Id)

    def salario_beneficio(media_salarios, FP):
        return round(media_salarios * FP, 2)

    salario_benef = salario_beneficio(media_cnis, FP)

    def renda_mensal_inicial(salario_beneficio, coef=1.0):
        return round(salario_beneficio * coef, 2)

    renda_inicial = renda_mensal_inicial(salario_benef, coef)

    # ===================
    # RESULTADOS DETALHADOS
    # ===================

    st.header("📑 Resultado Detalhado do Cálculo Previdenciário")
    st.write(f"**Média 80% CNIS:** R$ {media_cnis:,.2f}")
    st.write(f"**Média 80% Carta:** R$ {media_carta:,.2f}")
    st.write(f"**Fator Previdenciário:** {FP}")
    st.write(f"**Salário de Benefício:** R$ {salario_benef:,.2f}")
    st.write(f"**Renda Mensal Inicial (RMI):** R$ {renda_inicial:,.2f}")

    # ===================
    # ETAPA 6 - SALÁRIOS CRÍTICOS
    # ===================

    st.subheader("🚩 Salários DESCONSIDERADOS Identificados na Carta")
    desconsid = carta_df[carta_df.columns].apply(lambda x: x.astype(str).str.contains("DESCONSIDERADO", na=False)).any(axis=1)
    criticos = carta_df[desconsid]

    if not criticos.empty:
        st.dataframe(criticos)
        st.warning("Salários desconsiderados detectados. Pode haver impacto no cálculo. Recomenda-se revisão!")
    else:
        st.success("Nenhum salário desconsiderado identificado.")

    # ===================
    # EXPORTAÇÃO
    # ===================

    resultado_df = pd.DataFrame({
        'Fonte': ['CNIS', 'Carta'],
        'Média dos 80% maiores salários': [media_cnis, media_carta],
        'Fator Previdenciário': [FP, FP],
        'Salário de Benefício Calculado': [salario_benef, salario_benef],
        'Renda Mensal Inicial': [renda_inicial, renda_inicial]
    })

    st.download_button("📥 Exportar Resultado Final (CSV)", data=resultado_df.to_csv(index=False), file_name='resultado_inss_final.csv')

    # ===================
    # ENGENHARIA REVERSA EXPLICADA
    # ===================

    st.header("📚 Engenharia Reversa Aplicada")
    st.markdown("""
    - **Tempo de Contribuição (Tc):** 38 anos, 1 mês, 25 dias
    - **Expectativa de Sobrevida (Es):** 21,8 anos (IBGE)
    - **Idade do Segurado (Id):** 60 anos
    - **Alíquota Previdenciária (a):** 31%
    - **Coeficiente:** 100%

    **Fórmula Aplicada:**

    \[
    FP = \left(\frac{T_c \times a}{E_s}\right) \times \left(1 + \frac{(I_d + T_c \times a)}{100}\right)
    \]

    **Cálculo estruturado conforme Lei 8.213/91, Lei 9.876/99 e EC 103/19, respeitando metodologia previdenciária.**
    """)
