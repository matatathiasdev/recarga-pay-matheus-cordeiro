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
import warnings
import os

# IGNORAR ERROS
warnings.filterwarnings("ignore")

# TESTAR SE O WINUTILS ESTA FUNCIONANDO ANTES DE RODAR SPARK
subprocess.run(["winutils.exe", "ls", "C:\\tmp"])

# CAMINHO
path = str(Path().absolute()) + '\\datalake\\bronze\\transacoes'
output_path = str(Path().absolute()) + '\\datalake\\silver\\historico_saldo'
(Path().absolute() / "datalake" / "silver" / "historico_saldo").mkdir(parents=True, exist_ok=True)

# SESSÃO SPARK
# DEFININDO VARIAVEIS DE AMBIENTE
os.environ["HADOOP_HOME"] = r"C:\hadoop\hadoop-3.3.1"
os.environ["hadoop.home.dir"] = r"C:\hadoop\hadoop-3.3.1"
os.environ["PATH"] += r";C:\hadoop\hadoop-3.3.1\bin"

# INICIANDO SPARK
spark = SparkSession.builder.appName("spark-data").getOrCreate()

## HISTORICO E SALDO
### LER DADOS DA CAMADA BRUTO
df = spark.read.parquet(str(path))

### TABELA DE HISTORICO
df_hist = df.withColumn("amount", F.col("amount").cast("double"))\
            .withColumn("event_time", F.to_timestamp("event_time"))\
            .withColumn("cdc_sequence_num", F.col("cdc_sequence_num").cast("long"))


window_spec = w.partitionBy("account_id")\
               .orderBy("event_time", "cdc_sequence_num")

df_hist = df_hist.withColumn("row_num", 
                                F.row_number().over(window_spec))

### SALDO
df_saldo = df_hist.withColumn("balance",
                                F.sum("amount").over(window_spec))

### GRAVAR DADOS NO DATALAKE SIVER
df_saldo.write.mode("overwrite").parquet(output_path)

### GRAVAR DADOS NO BANCO DE DADOS DUCKDB DE CONSUMO
duck = db.DuckDB()
duck.drop_table('tb_saldo_historico')
duck.insert_data(df, 'tb_saldo_historico')
duck.close()