# BIBLIOTECAS DE APOIO
import sys
sys.path.append('./notebooks')

# BIBLIOTECAS
from datetime import timedelta, datetime as dt
from pyspark.sql import functions as F
from pyspark.sql.window import Window as w
from pyspark.sql import SparkSession
from pathlib import Path

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

# INICIANDO SPARK
spark = SparkSession.builder.appName("spark-data").getOrCreate()

# VARIAVEIS
taxa_juros = 0.01 

## CALCULO DE JUROS
### LER DADOS DA CAMADA SILVER
df = spark.read.parquet(str(path))

### CALCULO DIFERENCA EM HORASHORAS
df_juros = df.withColumn(
    "hours_since_mov",
    F.expr("round((unix_timestamp(current_timestamp()) - unix_timestamp(event_time)) / 3600)")
)

### CONDICOES PARA APLICAR JUROS
df_juros = df_juros.withColumn(
    "fees",
    F.when(
        (F.col("balance") > 100) & (F.col("hours_since_mov") >= 24),
        F.col("balance") * F.lit(taxa_juros)
    ).otherwise(0.0)
)

### NOVO SALDO COM JUROS
df_juros = df_juros.withColumn("updated_balance", F.col("balance") + F.col("fees"))\
                   .withColumn("tx_juros", F.lit(taxa_juros))

### GRAVAR DADOS NO DATALAKE SIVER
df_juros.write.mode("overwrite").parquet(output_path)

### GRAVAR DADOS NO BANCO DE DADOS DUCKDB DE CONSUMO
duck = db.DuckDB()
duck.drop_table('tb_saldo_juros')
duck.insert_data(df_juros, 'tb_saldo_juros')
duck.close()