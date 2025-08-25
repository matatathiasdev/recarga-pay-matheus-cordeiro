# BIBLIOTECAS DE APOIO
import subprocess
import sys

sys.path.append('./notebooks')

# GARANTE QUE USE O PYTHON ATUAL DO AMBIENTE VIRTUAL
PYTHON_EXEC = sys.executable

# TENTA INSTALAR O PIP SE NÃO EXISTIR
try:
    subprocess.check_call([PYTHON_EXEC, "-m", "ensurepip", "--upgrade"])
except subprocess.CalledProcessError:
    print("⚠️ Não foi possível instalar o pip com ensurepip.")

# ATUALIZA O PIP
try:
    subprocess.check_call([PYTHON_EXEC, "-m", "pip", "install", "--upgrade", "pip"])
except subprocess.CalledProcessError as e:
    print(f"❌ Falha ao atualizar pip: {e}")

# LISTA DE BIBLIOTECAS NECESSÁRIAS
bibliotecas = [
    'bs4',
    'beautifulsoup4',
    'requests',
    'pandas',
    'numpy',
    'openpyxl',
    'xlrd',
    'matplotlib',
    'duckdb',
    'pyspark',
    'pyparsing'
]

# INSTALA/ATUALIZA TODAS AS BIBLIOTECAS
for lib in bibliotecas:
    try:
        subprocess.check_call([PYTHON_EXEC, "-m", "pip", "install", "--upgrade", lib])
    except subprocess.CalledProcessError as e:
        print(f"❌ Falha ao instalar/atualizar {lib}: {e}")
