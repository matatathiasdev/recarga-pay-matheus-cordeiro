# 📊 Projeto de Dados - Recarga Pay

Este repositório contém a implementação de um **produto de dados** desenvolvido como parte de um teste técnico. O objetivo principal é **ingerir, processar e visualizar dados** utilizando PySpark, DuckDB e Streamlit.

---

## 📦 Estrutura do Projeto

```
recarga-pay-matheus-cordeiro/
│
├── notebooks/
│   ├── app.py              # Aplicação principal Streamlit
│   ├── nb_duck_db.py       # Classe de integração com DuckDB
│   ├── nb_valor_taxa.py    # Módulo para gravação e leitura de taxas
│   └── ...                 # Outros notebooks de apoio
│
├── requirements.txt        # Dependências do projeto
├── README.md               # Documentação principal
└── data/                   # Pasta destinada a arquivos de dados (não versionada)
```

---

## ⚙️ Instalação

### Pré-requisitos

* Python 3.10+
* [Poetry](https://python-poetry.org/) ou `pip`
* DuckDB >= 0.9
* PySpark >= 3.5
* Streamlit >= 1.35

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

Testes simples podem ser feitos executando:

```bash
pytest -v
```

*(se os testes unitários estiverem configurados em `tests/`)*

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
* **Manutenibilidade**: código separado em módulos (`nb_duck_db`, `nb_valor_taxa`).

---

## ⚖️ Trade-offs e Compromissos

* **DuckDB em vez de PostgreSQL**: escolhido pela simplicidade no teste, mas não ideal para ambiente produtivo.
* **Dados não versionados no repositório**: arquivos grandes foram omitidos para não inflar o GitHub.
* **Interface simples em Streamlit**: priorizada a entrega funcional em vez de design sofisticado.
* **Ausência de testes complexos**: devido a restrição de tempo, apenas testes básicos foram contemplados.

---

✍️ **Autor:** Matheus Rodrigues
