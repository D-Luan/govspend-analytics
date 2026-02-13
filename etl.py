import os
import zipfile
import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
from typing import Tuple
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

def get_env_variable(var_name: str) -> str:
    """
    Recupera variável de ambiente ou lança erro se não existir.
    """
    value = os.getenv(var_name)
    if not value:
        raise ValueError(f"A variável de ambiente '{var_name}' não está definida no arquivo .env")
    return value

DB_USER = get_env_variable("DB_USER")
DB_PASSWORD = get_env_variable("DB_PASSWORD")
DB_NAME = get_env_variable("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DB_CONNECTION_STRING = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
ZIP_FILE_PATH = DATA_DIR / "./202601_Despesas.zip"
EXTRACT_DIR = DATA_DIR / "raw"

MAPA_GERAL = {
    # Colunas para Dimensão Órgão
    'Código Órgão Subordinado': 'id_orgao_publico',
    'Código Órgão Superior': 'cod_orgao_superior',
    'Nome Órgão Superior': 'nome_orgao_superior',
    'Nome Órgão Subordinado': 'nome_orgao_subordinado',
    'Código Gestão': 'cod_gestao',
    'Nome Gestão': 'nome_gestao',
    
    # Colunas para Fato Despesas
    'Valor Empenhado (R$)': 'valor_empenhado',
    'Valor Pago (R$)': 'valor_pago',
    'Valor Liquidado (R$)': 'valor_liquido',
    'Valor Restos a Pagar Inscritos (R$)': 'valor_restos_inscritos',
    'Valor Restos a Pagar Pagos (R$)': 'valor_restos_pagos'
}

def extrair_dados(zip_path: Path, output_dir: Path) -> Path:
    """Extrai o ZIP e retorna o caminho do CSV."""
    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
        csv_files = [f for f in zip_ref.namelist() if f.endswith('.csv')]

        if not csv_files:
            raise FileExistsError("Nenhum CSV encontrado no ZIP.")
        return output_dir / csv_files[0]
    
def transformar_dados(csv_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Lê o CSV, aplica filtros de negócio e separa em Dimensão e Fato.
    """
    print("Lendo arquivo CSV...")
    colunas_interesse = list(MAPA_GERAL.keys())
    df = pd.read_csv(csv_path, usecols=colunas_interesse, sep=';', encoding='ISO-8859-1', decimal=',')

    df_renomeado = df.rename(columns=MAPA_GERAL)

    cols_float = ['valor_liquido', 'valor_pago']
    for col in cols_float:
        if col in df_renomeado.columns:
            df_renomeado[col] = pd.to_numeric(df_renomeado[col], errors='coerce').fillna(0.0)

    print("Aplicando filtros de negócio...")
    filtro_zeros = ~((df_renomeado['valor_liquido'] == 0.00) & (df_renomeado['valor_pago'] == 0.00))
    df_clean = df_renomeado[filtro_zeros].copy()

    print("Construindo Dimensão Órgão...")
    cols_dim = [
        'id_orgao_publico', 'cod_orgao_superior', 'nome_orgao_superior',
        'cod_orgao_subordinado', 'nome_orgao_subordinado', 
        'cod_gestao', 'nome_gestao'
    ]

    df_clean['cod_orgao_subordinado'] = df_clean['id_orgao_publico']

    cols_dim_existentes = [c for c in cols_dim if c in df_clean.columns]
    df_dim = df_clean[cols_dim_existentes].drop_duplicates(subset=['id_orgao_publico'])

    print("Construindo Fato Despesas...")
    cols_fato = [
        'id_orgao_publico', 'valor_empenhado', 'valor_pago', 
        'valor_restos_inscritos', 'valor_restos_pagos'
    ]
    cols_fato_existentes = [c for c in cols_fato if c in df_clean.columns]
    df_fato = df_clean[cols_fato_existentes]

    return df_dim, df_fato

def carregar_dados(df_dim: pd.DataFrame, df_fato: pd.DataFrame):
    """Insere os dados no Banco SQL via SQLAlchemy."""
    print("Conectando ao banco de dados...")
    engine = create_engine(DB_CONNECTION_STRING)

    with engine.begin() as connection:
        connection.execute(text("TRUNCATE TABLE dim_orgao_public, fato_despesas RESTART IDENTITY CASCADE;"))
        
        print(f"Inserindo {len(df_dim)} registros na dim_orgao_public...")
        df_dim.to_sql('dim_orgao_public', connection, if_exists='append', index=False, method='multi', chunksize=10000)

        print(f"Inserindo {len(df_fato)} registros na fato_despesas...")
        df_fato.to_sql('fato_despesas', connection, if_exists='append', index=False, method='multi', chunksize=10000)

def run_etl():
    try:
        print("Iniciando ETL")

        csv_path = extrair_dados(ZIP_FILE_PATH, EXTRACT_DIR)
        print(f"Extração concluída: {csv_path.name}")

        df_dim, df_fato = transformar_dados(csv_path)
        print(f"Transformação concluída.")
        print(f"Dimensão: {len(df_dim)} linhas únicas | Fato: {len(df_fato)} linhas.") 

        carregar_dados(df_dim, df_fato)
        print("Carga concluída com sucesso.")

        print("ETL Finalizado")
    
    except Exception as e:
        print(f"\nERRO CRÍTICO: {e}")

if __name__ == "__main__":
    DATA_DIR.mkdir(exist_ok=True)
    if not ZIP_FILE_PATH.exists():
        print(f"AVISO: Coloque o arquivo ZIP em: {DATA_DIR}")
    else:
        run_etl()