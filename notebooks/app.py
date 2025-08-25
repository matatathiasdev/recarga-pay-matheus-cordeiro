# BIBLIOTECAS DE APOIO
import sys
import os
sys.path.append('./notebooks')

script_path = 'notebooks/nb_libs.py'
os.system(f"python {script_path}")

from pathlib import Path

import nb_valor_taxa as tx
import nb_duck_db as db
import streamlit as st
import pandas as pd


## STREAMLIT
# LAYOUT DA PAGINA
st.set_page_config(
    page_title="Painel de Visualização DuckDB",
    page_icon="📊",
    layout="wide",
)

# TITULO DA PAGINA
st.title("Visualizador DuckDB")

# CRIA O MENU LATERAL DE FILTROS
st.sidebar.title('Painel de Controle')

# LIMPAR FILTRO DE TAXA
slider_container = st.sidebar.empty()
if 'vl_reg' not in st.session_state:
    st.session_state['vl_reg'] = 1

def run_script(valor):
    dict_path = {
        0: 'notebooks/nb_libs.py',
        1: 'notebooks/nb_dados_brutos.py',
        2: 'notebooks/nb_hist_saldo_silver.py',
        3: 'notebooks/nb_saldo_juros_silver.py'
    }

    script_path = dict_path.get(valor)

    # VERIFICAR SE O ARQUIVO EXISTE
    if os.path.exists(script_path):
        os.system(f"python {script_path}")
        st.success(f"Script {script_path} executado com sucesso!")
    else:
        st.error(f"O arquivo {script_path} não foi encontrado.")
 

caminho = Path().absolute() / "datalake"
if os.path.exists(caminho)== False:
    run_script(1)
    run_script(2)
    run_script(3)

# BOTAO PARA ATUALIZAR OS DADOS BRUTOS
if st.sidebar.button('Atualizar dados Brutos', use_container_width=True):
    run_script(1)

# BOTAO PARA ATUALIZAR OS DADOS HISTORICOS SALDO
if st.sidebar.button('Atualizar dados Historico e Saldo', use_container_width=True):
    run_script(2)

# BOTAO PARA ATUALIZAR OS DADOS SALDO JUROS
if st.sidebar.button('Atualizar dados Saldo e Juros', use_container_width=True):
    run_script(3)

# SLIDER PARA FILTRAR A TAXA DE JUROS
with st.sidebar:
    st.slider('Taxa de Juro', 1, 30, key='vl_taxa', label_visibility='visible')
    taxa = st.session_state['vl_taxa']
    tx.ValorTaxa(taxa).atualizar_taxa()

# SCHEMA DO BANCO DE DADOS
st.subheader("Schema do Banco de Dados")
df = db.DuckDB().select_from_duckdb("SELECT * FROM information_schema.tables")
st.dataframe(df)

# CONSULTAR DADOS
query = st.text_area("Escreva sua query SQL:", "SELECT * FROM minha_tabela LIMIT 10")
if st.button("Executar"):
    df = db.DuckDB().select_from_duckdb(query)
    st.dataframe(df)
