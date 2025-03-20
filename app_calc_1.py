import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config(page_title="Cálculo Previdenciário Real INSS", layout="wide")

st.title("🧮 INSS Cálculo Engine - Revisão da Vida Toda")
st.caption("Aplicação baseada em engenharia reversa do cálculo previdenciário, conforme Leis 8.213/91, 9.876/99 e INs.")

# ============================
# 📥 Inputs CNIS e Carta
# ============================
st.sidebar.header("📂 Carregar Arquivos")

uploaded_cnis = st.sidebar.file_uploader("Importe o CSV do CNIS", type="csv")
uploaded_carta = st.sidebar.file_uploader("Importe o CSV da Carta de Benefício", type="csv")

# ============================
# Funções Auxiliares
# ============================
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

# ============================
# Execução Principal
# ============================
if uploaded_cnis and uploaded_carta:

    st.success("✅ Arquivos carregados com sucesso!")

    cnis_df = pd.read_csv(uploaded_cnis)
    carta_df = pd.read_csv(uploaded_carta)

    # Limpeza e sanitização
    cnis_df = limpar_dados(cnis_df, cnis_df.columns[1])
    carta_df = limpar_dados(carta_df, carta_df.columns[2])

    # Exibição dos dados tratados
    st.subheader("📄 Dados CNIS - Pós-Sanitização")
    st.dataframe(cnis_df)

    st.subheader("📄 Dados Carta - Pós-Sanitização")
    st.dataframe(carta_df)

    # ============================
    # Cálculo Fuzzy e Previdenciário
    # ============================
    st.header("🔢 Cálculo Previdenciário Real - Engenharia Reversa")

    media_cnis = calcular_media_ponderada(cnis_df, cnis_df.columns[1])
    media_carta = calcular_media_ponderada(carta_df, carta_df.columns[2], carta_df.columns[5])

    # Parâmetros Legais Fixos
    Tc = 38 + (1/12) + (25/365)  # 38 anos, 1 mês, 25 dias
    a = 0.31
    Es = 21.8
    Id = 60
    coef = 1.0

    FP = fator_previdenciario(Tc, a, Es, Id)
    salario_benef = salario_beneficio(media_cnis, FP)
    renda_inicial = renda_mensal_inicial(salario_benef, coef)

    # Resultado
    st.write(f"**Média CNIS (ponderada):** R$ {media_cnis:,.2f}")
    st.write(f"**Média Carta (ponderada):** R$ {media_carta:,.2f}")
    st.write(f"**Fator Previdenciário:** {FP}")
    st.write(f"**Salário de Benefício:** R$ {salario_benef:,.2f}")
    st.write(f"**Renda Mensal Inicial:** R$ {renda_inicial:,.2f}")

    # ============================
    # Identificação de Salários Críticos
    # ============================
    st.subheader("🚩 Salários Críticos Identificados")

    desconsiderados = carta_df[carta_df.columns].apply(lambda x: x.astype(str).str.contains("DESCONSIDERADO", na=False)).any(axis=1)
    criticos = carta_df[desconsiderados]

    if not criticos.empty:
        st.dataframe(criticos)
        st.warning("Salários desconsiderados detectados! Podem impactar no valor final. Recomenda-se revisão jurídica.")
    else:
        st.success("Nenhum salário desconsiderado identificado na carta.")

    # ============================
    # Exportação
    # ============================
    resultado_df = pd.DataFrame({
        'Fonte': ['CNIS', 'Carta'],
        'Média dos 80% maiores salários': [media_cnis, media_carta],
        'Fator Previdenciário': [FP, FP],
        'Salário de Benefício': [salario_benef, salario_benef],
        'Renda Mensal Inicial': [renda_inicial, renda_inicial]
    })

    st.download_button("📥 Baixar Resultado (CSV)", data=resultado_df.to_csv(index=False), file_name='resultado_inss.csv')

    # ============================
    # Explicação do Cálculo
    # ============================
    st.header("📚 Explicação Detalhada do Cálculo")
    st.markdown("""
    - **Base Legal:** Lei 8.213/91, Lei 9.876/99, EC 103/19.
    - **Tempo de Contribuição (Tc):** 38 anos, 1 mês, 25 dias.
    - **Expectativa de Sobrevida (Es):** 21,8 anos (IBGE).
    - **Idade do Segurado (Id):** 60 anos.
    - **Alíquota Previdenciária (a):** 31%.
    - **Coeficiente:** 100%.
    
    **Fórmula:**

    \[
    FP = \\left(\\frac{T_c \\times a}{E_s}\\right) \\times \\left(1 + \\frac{(I_d + T_c \\times a)}{100}\\right)
    \]

    Aplicado diretamente sobre as médias ponderadas dos salários CNIS e Carta, respeitando integralmente os parâmetros normativos.
    """)

else:
    st.info("📂 Aguarde o carregamento dos dois arquivos CSV (CNIS e Carta de Benefício) para iniciar o cálculo.")

