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
subprocess.run(["winutils.exe", "ls", "C:\\tmp"])

# CAMINHO
path = str(Path().absolute()) + '\\interviews_fake_transactions'

output_path = str(Path().absolute()) + '\\datalake\\bronze\\transacoes'
(Path().absolute() / "datalake" / "bronze" / "transacoes").mkdir(parents=True, exist_ok=True)

# SESSÃO SPARK
# DEFININDO VARIAVEIS DE AMBIENTE
path_hadoop = str(Path().absolute()) + '\\hadoop'
os.environ["HADOOP_HOME"] = path_hadoop + "\\hadoop-3.3.1"
os.environ["hadoop.home.dir"] = path_hadoop + "\\hadoop-3.3.1"
os.environ["PATH"] += ";" + path_hadoop + "\\hadoop\hadoop-3.3.1\bin"

# INICIANDO SPARK
spark = SparkSession.builder.appName("spark-data").getOrCreate()

## DATALAKE BRUTO
### LER ARQUIVOS DISPONIBILIZADOS
df = spark.read.parquet(path)

### GRAVAR DADOS NO DATALAKE
df.write.mode("overwrite").parquet(output_path)

### GRAVAR DADOS NO BANCO DE DADOS DUCKDB DE CONSUMO
duck = db.DuckDB()
duck.drop_table('tb_transacoes')
duck.insert_data(df, 'tb_transacoes')
duck.close()