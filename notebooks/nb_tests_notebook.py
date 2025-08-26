# BIBLIOTECAS DE APOIO
import sys
sys.path.append('./notebooks')

# BIBLIOTECAS
from datetime import timedelta, datetime as dt
from pyspark.sql import functions as F
from pyspark.sql.window import Window as w
from pyspark.sql import SparkSession
from pathlib import Path

import nb_valor_taxa as tx
import nb_duck_db as db
import pandas as pd
import subprocess
import requests
import warnings
import os

# Iniciar sessão Spark
spark = SparkSession.builder.appName("testes-pipeline").getOrCreate()

print("✅ Spark inicializado com sucesso")

# -------------------------------
# 1. TESTE DUCKDB - CRIAR E CONSULTAR TABELA
# -------------------------------
duck = db.DuckDB()

# Criar dataframe pequeno
data = [(1, "2025-01-01 10:00:00", 100.0),
        (2, "2025-01-02 12:00:00", 200.0)]
df = spark.createDataFrame(data, ["account_id", "event_time", "balance"])

# Inserir no DuckDB
duck.drop_table("tb_teste")
duck.insert_data(df, "tb_teste")

# Consultar de volta
df_out = duck.select_from_duckdb("SELECT * FROM tb_teste")
print(df_out)

assert len(df_out) == 2
print("✅ Teste DuckDB: OK")

# -------------------------------
# 2. TESTE SALDO ACUMULADO SIMPLES
# -------------------------------
from pyspark.sql import functions as F, Window

window_spec = Window.partitionBy("account_id").orderBy("event_time")
df_saldo = df.withColumn("balance_acc", F.sum("balance").over(window_spec))

df_saldo.show()
assert "balance_acc" in df_saldo.columns
print("✅ Teste saldo acumulado: OK")

# -------------------------------
# 3. TESTE JUROS COM VALORTAXA
# -------------------------------
taxa = tx(10)  # 10% de juros
taxa.atualizar_taxa()

df_juros = spark.read.parquet("datalake/silver/saldo_juros")
df_juros.show(5)

assert "fees" in df_juros.columns
print("✅ Teste juros com ValorTaxa: OK")

print("\n🎉 TODOS OS TESTES RODARAM COM SUCESSO!")
