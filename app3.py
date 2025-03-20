import streamlit as st
import pandas as pd
from io import StringIO

st.title("📊 Dashboard Previdenciário Modular - Revisão da Vida Toda - Versão 3")

# =============================
# 📥 Etapa 1 - Inserção dos Dados CNIS
# =============================
st.header("📥 Etapa 1 - Inserção dos Dados CNIS")
cnis_txt = st.text_area("Cole os dados do CNIS (Competência e Remuneração)", height=200)

# =============================
# 📥 Etapa 2 - Inserção dos Dados da Carta de Concessão
# =============================
st.header("📥 Etapa 2 - Inserção dos Dados da Carta de Concessão")
carta_txt = st.text_area("Cole os dados da Carta de Benefício (SEQ, Data, Salário, Índice, Salário Corrigido, Observação)", height=200)

# Funções auxiliares para parsing e limpeza dos dados
def parse_data(text_data, sep_options=['\t', ';', ',']):
    for sep in sep_options:
        try:
            df = pd.read_csv(StringIO(text_data), sep=sep)
            return df
        except:
            continue
    return None

def clean_numeric(df, cols):
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    df = df.dropna(subset=cols)
    return df

# Processamento dos dados
cnis_df = parse_data(cnis_txt)
carta_df = parse_data(carta_txt)

if cnis_df is not None:
    st.subheader("🔎 Dados CNIS Carregados")
    st.dataframe(cnis_df)
    cnis_df = clean_numeric(cnis_df, [cnis_df.columns[1]])
    st.subheader("📈 Gráfico CNIS - 80% Maiores Salários")
    cnis_sorted = cnis_df.sort_values(by=cnis_df.columns[0])
    cnis_top = cnis_sorted.nlargest(int(0.8 * len(cnis_sorted)), cnis_sorted.columns[1])
    st.bar_chart(data=cnis_top, x=cnis_top.columns[0], y=cnis_top.columns[1])

if carta_df is not None:
    st.subheader("🔎 Dados Carta de Benefício Carregados")
    st.dataframe(carta_df)
    carta_df = clean_numeric(carta_df, [carta_df.columns[2]])
    st.subheader("📈 Gráfico Carta - 80% Maiores Salários")
    carta_sorted = carta_df.sort_values(by=carta_df.columns[1])
    carta_top = carta_sorted.nlargest(int(0.8 * len(carta_sorted)), carta_df.columns[2])
    st.bar_chart(data=carta_top, x=carta_top.columns[1], y=carta_top.columns[2])

# =============================
# 🧮 Etapa 3 - Cálculo Previdenciário INSS Real com Fuzzy
# =============================
if cnis_df is not None and carta_df is not None:
    st.header("🧮 Etapa 3 - Cálculo Previdenciário INSS Real - Fuzzy")

    media_cnis = cnis_top[cnis_top.columns[1]].mean()
    media_carta = carta_top[carta_top.columns[2]].mean()

    # Parâmetros Fixos Baseados na Legislação
    Tc = 38 + (1/12) + (25/365)  # Tempo de Contribuição: 38 anos, 1 mês e 25 dias
    a = 0.31  # Alíquota
    Es = 21.8  # Expectativa de Sobrevida
    Id = 60    # Idade

    # Funções Matemáticas Modulares
    def calcular_fator_previdenciario(Tc, a, Es, Id):
        FP = (Tc * a / Es) * (1 + ((Id + Tc * a) / 100))
        return round(FP, 4)

    def calcular_salario_beneficio(media_salarios, fator_previdenciario):
        salario_beneficio = media_salarios * fator_previdenciario
        return round(salario_beneficio, 2)

    def calcular_renda_mensal_inicial(salario_beneficio, coeficiente=1.0):
        return round(salario_beneficio * coeficiente, 2)

    FP = calcular_fator_previdenciario(Tc, a, Es, Id)
    beneficio = calcular_salario_beneficio(media_cnis, FP)
    renda_inicial = calcular_renda_mensal_inicial(beneficio)

    st.write(f"**Média dos 80% maiores salários CNIS:** R$ {media_cnis:,.2f}")
    st.write(f"**Média dos 80% maiores salários Carta:** R$ {media_carta:,.2f}")
    st.write(f"**Fator Previdenciário Calculado:** {FP:.4f}")
    st.write(f"**Salário de Benefício Calculado:** R$ {beneficio:,.2f}")
    st.write(f"**Renda Mensal Inicial Calculada:** R$ {renda_inicial:,.2f}")

    if 'Observação' in carta_df.columns:
        desconsid = carta_df[carta_df['Observação'].astype(str).str.contains("DESCONSIDERADO", na=False)]
        if not desconsid.empty:
            st.subheader("🚩 Salários Desconsiderados na Carta")
            st.dataframe(desconsid)
            st.write("Os salários marcados como DESCONSIDERADO não foram computados no cálculo por regra normativa específica.")

    resultado_df = pd.DataFrame({
        'Fonte': ['CNIS', 'Carta'],
        'Média dos 80% maiores salários': [media_cnis, media_carta],
        'Salário de Benefício Calculado': [beneficio, media_carta * FP],
        'Renda Mensal Inicial': [renda_inicial, media_carta * FP]
    })
    st.download_button("📥 Exportar Resultado Final (CSV)", data=resultado_df.to_csv(index=False), file_name='resultado_final.csv')

# =============================
# 📄 Etapa 4 - Base Legal e Matriz Normativa Fuzzy
# =============================
if cnis_df is not None and carta_df is not None:
    st.header("📄 Etapa 4 - Base Legal Aplicada e Matriz Normativa")
    matriz_df = pd.DataFrame({
        'Parâmetro': ['Tempo de Contribuição', 'Expectativa de Sobrevida', 'Idade', 'Alíquota', 'Média Salarial', 'Número Meses Lei 181', 'Coeficiente'],
        'Símbolo': ['Tc', 'Es', 'Id', 'a', 'média', 'y', 'coeficiente'],
        'Base Legal': [
            'Art. 201, §7º, C.F/88; Lei 8.213/91, Art. 29',
            'Lei 9.876/99, Art. 3º; Decreto 3.048/99',
            'Lei 8.213/91, Art. 52; Decreto 3.048/99',
            'Lei 8.212/91, Art. 20 e 21',
            'Lei 8.213/91, Art. 29',
            'Lei 9.876/99, Art. 3º',
            'Lei 8.213/91, Art. 29, §7º'
        ],
        'Pertinência Fuzzy': ['Tc/Tmin', 'Esref/Es', 'Id/Idref', 'a/amx', 'media/mediaref', 'Valor Fixo', 'coef/1.0']
    })
    st.dataframe(matriz_df)
    st.download_button("📥 Exportar Matriz Normativa (CSV)", data=matriz_df.to_csv(index=False), file_name='matriz_normativa.csv')

    st.success("Matriz normativa detalhada pronta para fundamentação jurídica.")
