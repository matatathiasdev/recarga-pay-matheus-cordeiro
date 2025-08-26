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

# IGNORAR ERROS
warnings.filterwarnings("ignore")

# TESTAR SE O WINUTILS ESTA FUNCIONANDO ANTES DE RODAR SPARK
# CAMINHO PARA O WINUTILS
winutils_path = r"C:\hadoop\hadoop-3.3.1\bin\winutils.exe"

# TESTA APENAS SE EXISTE
if os.path.exists(winutils_path):
    subprocess.run([winutils_path, "ls", "C:\\tmp"])
else:
    print("winutils.exe não encontrado. Pulando teste.")

# CAMINHO
path = str(Path().absolute()) + '\\datalake\\silver\\historico_saldo'
output_path = str(Path().absolute()) + '\\datalake\\silver\\saldo_juros'
(Path().absolute() / "datalake" / "silver" / "saldo_juros").mkdir(parents=True, exist_ok=True)

# SESSÃO SPARK
# DEFININDO VARIAVEIS DE AMBIENTE
os.environ["HADOOP_HOME"] = r"C:\hadoop\hadoop-3.3.1"
os.environ["hadoop.home.dir"] = r"C:\hadoop\hadoop-3.3.1"
os.environ["PATH"] += r";C:\hadoop\hadoop-3.3.1\bin"

# TESTAR SESSÃO SPARK
spark = SparkSession.builder.appName("testes-pipeline").getOrCreate()
print("✅ Spark inicializado com sucesso")

# -------------------------------
# 1. TESTE DUCKDB - CRIAR E CONSULTAR TABELA
# -------------------------------
duck = db.DuckDB()

# Criar dataframe pequeno
### LER DADOS DA CAMADA SILVER
df = spark.read.parquet(str(path)).limit(10).select("account_id", "event_time", "balance")

duck.drop_table("tb_teste")
duck.insert_data(df, "tb_teste")

# Consultar de volta
df_out = duck.select_from_duckdb("SELECT * FROM tb_teste")
print(df_out)
print("✅ Teste DuckDB: OK")

duck = db.DuckDB()
duck.drop_table("tb_teste")

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
taxa = tx.ValorTaxa(10)  # 10% de juros
taxa.atualizar_taxa()

df_juros = spark.read.parquet("datalake/silver/saldo_juros")
df_juros.show(5)

assert "fees" in df_juros.columns
print("✅ Teste juros com ValorTaxa: OK")

print("\n🎉 TODOS OS TESTES RODARAM COM SUCESSO!")