## BIBLIOTECAS
from pyspark.sql import DataFrame as SparkDataFrame
from pyspark.sql import functions as F
from pyspark.sql import SparkSession
from pathlib import Path

import pandas as pd
import subprocess
import warnings
import tempfile
import duckdb
import time
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

# SESSÃO SPARK
# DEFININDO VARIAVEIS DE AMBIENTE
os.environ["HADOOP_HOME"] = r"C:\hadoop\hadoop-3.3.1"
os.environ["hadoop.home.dir"] = r"C:\hadoop\hadoop-3.3.1"
os.environ["PATH"] += r";C:\hadoop\hadoop-3.3.1\bin"

class DuckDB:
    def __init__(self):
        # CRIA O BANCO DE DADOS
        self.db_folder = Path().absolute() / "data" 
        self.db_folder.mkdir(parents=True, exist_ok=True)

        self.db_path = self.db_folder / "db_consumo.duckdb" 
        self.db_path = str(self.db_path)

        self.con = duckdb.connect(self.db_path)
        
        # INICIANDO SPARK
        self.spark = SparkSession.builder.appName("spark-data-duck").getOrCreate()

    def close(self):
        # FECHA A CONEXAO COM O BANCO DE DADOS
        self.con.close()
    
    def drop_table(self, table_name):
        # DROPAR A TABELA SE EXISTIR
        self.con.execute(f"DROP TABLE IF EXISTS {table_name}") 

    def delete_table_from_duckdb(self, query: str):
        # DELETA A TABELA
        self.con.execute(query)
        self.con.close()
    
    def select_from_duckdb(self, query: str) -> pd.DataFrame:
           try:
               # EXECUTA A QUERY E RETORNA O RESULTADO EM UM DATAFRAME
               df = self.con.execute(query).fetchdf()
               return df
           except duckdb.CatalogException as e:
                # print(f"Erro de catálogo ao executar a query: {e}")
                return None
           finally:
                self.con.close()

    def insert_data(self, df: SparkDataFrame, table_name: str):
        # SALVA SPARK DF COMO PARQUET TEMPORARIO
        with tempfile.TemporaryDirectory(dir=Path().absolute())  as tmpdir:
            time.sleep(10)

            parquet_path = os.path.join(tmpdir, "tmp.parquet")
            df.write.mode("overwrite").parquet(parquet_path)
            
            tmpdir = tmpdir.replace("\\", "/")
            time.sleep(2)

            # VERIFICA SE A TABELA JA EXISTE
            tabela_existe = self.con.execute(f"""
                SELECT 1 
                FROM information_schema.tables 
                WHERE table_name = '{table_name}'
                LIMIT 1
            """).fetchone() is not None

            if tabela_existe:
                self.con.execute(f"INSERT INTO {table_name} SELECT * FROM parquet_scan('{parquet_path}/*.parquet')")
            else:
                self.con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM parquet_scan('{parquet_path}/*.parquet')")

            

