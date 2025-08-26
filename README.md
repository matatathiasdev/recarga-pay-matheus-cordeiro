# 📊 Projeto de Dados - Recarga Pay

Este repositório contém a implementação de um **produto de dados** desenvolvido como parte de um teste técnico. O objetivo principal é **ingerir, processar e visualizar dados** utilizando PySpark, DuckDB e Streamlit.

---

## 📦 Estrutura do Projeto

```
recarga-pay-matheus-cordeiro/
│
├── notebooks/
│   ├── app.py                      # Aplicação principal em Streamlit
│   ├── nb_libs.py                  # Instala e garante dependências
│   ├── nb_duck_db.py               # Classe de integração com DuckDB
│   ├── nb_dados_brutos.py          # Ingestão de dados brutos (camada bronze)
│   ├── nb_hist_saldo_silver.py     # Processamento histórico de saldo (camada silver)
│   ├── nb_saldo_juros_silver.py    # Cálculo de juros sobre saldo (camada silver)
│   ├── nb_valor_taxa.py            # Classe para atualizar taxa de juros dinamicamente
│   └── nb_tests_notebook.py        # Notebook/script de testes automatizados simples
│
├── requirements.txt                # Dependências do projeto
├── artifacts/                      # Pasta destinada a armazenar arquivos temporarios do Spark (não vercionada)
├── data/                           # Pasta destinada a o banco de dados DuckDB (não versionada)
├── datalake/                       # Pasta destinada a arquivos de dados do Spark (não versionada)
├── hadoop/                         # Pasta destinada aos arquivos de configuracao do Hadoop
├── interviews_fake_transactions/   # Pasta destinada aos arquivos de base disponibilizados para RecargaPay
└── README.md                       # Documentação principal
```

### 📖 Descrição dos Notebooks / Módulos

#### `app.py`

* Arquivo principal da aplicação.
* Implementado em **Streamlit**, responsável por criar a interface web.
* Permite visualizar dados processados a partir do DuckDB.
* Possui botões para executar os scripts de ingestão e transformação (`nb_dados_brutos.py`, `nb_hist_saldo_silver.py`, `nb_saldo_juros_silver.py`).
* Inclui um **slider** para ajustar dinamicamente a taxa de juros via `nb_valor_taxa.py`.
* Exibe o **schema do banco** e permite executar queries SQL customizadas.

#### `nb_libs.py`

* Script utilitário para garantir que todas as dependências estão instaladas.
* Instala/atualiza bibliotecas essenciais como `pandas`, `numpy`, `pyspark`, `duckdb`.
* Executado automaticamente pelo `app.py` no início da aplicação.

#### `nb_duck_db.py`

* Contém a classe `DuckDB` que centraliza a integração com o banco **DuckDB**.
* Funções principais:

  * Criar banco e conectar.
  * Executar queries (`select_from_duckdb`).
  * Criar/atualizar tabelas com DataFrames do Spark.
  * Gravar dados via Parquet temporário.
  * Dropar tabelas e fechar conexões.
* Atua como camada de persistência de dados de consumo.

#### `nb_dados_brutos.py`

* Responsável pela ingestão da camada **bronze**.
* Lê arquivos **Parquet** de transações brutas (`interviews_fake_transactions`).
* Grava os dados na estrutura de **datalake/bronze/transacoes**.
* Persiste os dados no DuckDB na tabela `tb_transacoes`.
* Garante a criação da pasta e substituição dos dados em execuções subsequentes.

#### `nb_hist_saldo_silver.py`

* Responsável por criar a camada **silver** de **histórico de saldo**.
* Lê a camada bronze de transações.
* Converte colunas para tipos corretos (ex: `amount`, `event_time`, `cdc_sequence_num`).
* Cria janela particionada por `account_id` para calcular **ordenação temporal**.
* Gera histórico de movimentações (`df_hist`).
* Calcula **saldo acumulado** (`df_saldo`).
* Grava saída no **datalake/silver/historico\_saldo** e no DuckDB (`tb_saldo_historico`).

#### `nb_saldo_juros_silver.py`

* Responsável por calcular **juros** sobre saldos (camada **silver**).
* Lê dados do histórico de saldo (`silver/historico_saldo`).
* Calcula tempo desde a última movimentação em horas (`hours_since_mov`).
* Aplica taxa de juros fixa (0.01) para saldos acima de 100 e com mais de 24h sem movimentação.
* Cria novo saldo atualizado (`updated_balance`).
* Grava saída em **datalake/silver/saldo\_juros** e no DuckDB (`tb_saldo_juros`).

#### `nb_valor_taxa.py`

* Define a classe `ValorTaxa` que permite **ajustar dinamicamente** a taxa de juros.
* Instanciada com a taxa definida pelo usuário (via Streamlit).
* Executa o mesmo fluxo de cálculo de juros do `nb_saldo_juros_silver.py`, mas aplicando a taxa escolhida.
* Atualiza os dados no **datalake/silver/saldo\_juros** e na tabela DuckDB `tb_saldo_juros`.

#### `nb_tests_notebook.py`

* Contém **testes automatizados simples** para validar o pipeline.
* Principais testes incluídos:

  * Criar e consultar tabela no DuckDB.
  * Calcular saldo acumulado com janela de partição.
  * Executar `ValorTaxa` com taxa de 10% e validar a criação da coluna `fees`.
* Exibe mensagens de sucesso para cada teste.

---

## ⚙️ Instalação

### Pré-requisitos

* Python 3.10+
* [Poetry](https://python-poetry.org/) ou `pip`
* DuckDB >= 0.9
* PySpark >= 3.5
* Streamlit >= 1.35

### Spark

* **Java**: Instalar Java 8 ou Java 11: https://www.azul.com/downloads/?package=jdk#download-openjdk.
* **Variável de ambiente do Java:** 
```bash
setx JAVA_HOME "C:\Program Files\Zulu\zulu-11"
```

### Hadoop
* **Baixar o Hadoop 3.3.1**: https://github.com/cdarlint/winutils.
* **Pasta Hadoop**: Deixei a pasta dentro do projeto para facilitar na configuracao mais nao e o idea! O mais correto era criar uma pasta em: `C:\hadoop` 


### Instalação com `pip`

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### Instalação com `poetry`

```bash
poetry install
```

---

## ▶️ Execução

1. **Configurar os dados**
   Coloque seus arquivos de dados grandes (CSV/Parquet) na pasta `data/`.

2. **Executar o Streamlit**

   ```bash
   streamlit run notebooks/app.py
   ```

3. **Interface**
   A aplicação abrirá no navegador em `http://localhost:8501`.

---

## 🧪 Testes

Este projeto inclui um script/notebook de testes: `notebooks/nb_tests_notebook.py`.

### Como executar os testes

```bash
python notebooks/nb_tests_notebook.py
```

### Testes incluídos

* **Teste DuckDB**: cria e consulta tabela `tb_teste`.
* **Teste de saldo acumulado**: valida cálculo de saldo progressivo.
* **Teste de juros com ValorTaxa**: aplica taxa de 10% e verifica coluna `fees`.

Esses testes são básicos, mas garantem o funcionamento essencial do pipeline. Para produção, recomenda-se evoluir com `pytest` e frameworks de qualidade de dados como **Great Expectations**.

---

## 🗄️ Recomendações para Ingestão em Banco Transacional

* **Produção**: evitar DuckDB como banco final, usar PostgreSQL ou SQL Server.
* **Ingestão em lote**:

  * Exportar dados processados para arquivos Parquet particionados.
  * Utilizar ferramenta de orquestração (Airflow/Databricks Jobs) para carga incremental.
* **Ingestão em streaming**:

  * Usar Spark Structured Streaming conectado a Kafka ou EventHub.
  * Persistir em tabelas de staging antes da normalização.
* **Boas práticas**:

  * Definir chaves primárias e índices adequados.
  * Controlar versionamento de dados (SCD tipo 2).
  * Monitorar qualidade dos dados antes da carga.

---

## 🏗️ Escolhas de Design

### Funcionais

* **PySpark**: utilizado para manipulação de grandes volumes de dados com eficiência.
* **DuckDB**: escolhido como banco analítico local para persistência leve e consultas rápidas.
* **Streamlit**: fornece visualização simples e interativa para explorar os resultados.

### Não Funcionais

* **Escalabilidade**: arquitetura modular que permite troca de banco (DuckDB → PostgreSQL) facilmente.
* **Performance**: leitura em Parquet e uso de Spark para paralelismo.
* **Manutenibilidade**: código separado em módulos para ingestão, transformação e consumo.

---

## ⚖️ Trade-offs e Compromissos

* **DuckDB em vez de PostgreSQL**: escolhido pela simplicidade no teste, mas não ideal para ambiente produtivo.
* **Dados não versionados no repositório**: arquivos grandes foram omitidos para não inflar o GitHub.
* **Interface simples em Streamlit**: priorizada a entrega funcional em vez de design sofisticado.
* **Ausência de testes complexos**: devido a restrição de tempo, apenas testes básicos foram contemplados.

---

✍️ **Autor:** Matheus Rodrigues
- [LinkedIn](https://www.linkedin.com/in/matheus-rodrigues-106319b7/)  
- [E-mail](mailto:matheus.rodrigues_santos@hotmail.com)
