import os
from typing import List, Optional
from decimal import Decimal
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Field, Session, select, create_engine, Relationship
from dotenv import load_dotenv
from etl import get_env_variable

load_dotenv()

DB_USER = get_env_variable("DB_USER")
DB_PASSWORD = get_env_variable("DB_PASSWORD")
DB_NAME = get_env_variable("DB_NAME")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DB_CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DB_CONNECTION_STRING, echo=False)

class DimOrgaoPublic(SQLModel, table=True):
    __tablename__ = "dim_orgao_public"

    id_orgao_publico: int = Field(primary_key=True)
    cod_orgao_superior: Optional[str] = None
    nome_orgao_superior: Optional[str] = None
    cod_orgao_subordinado: Optional[str] = None
    nome_orgao_subordinado: Optional[str] = None
    cod_gestao: Optional[str] = None
    nome_gestao: Optional[str] = None

class FatoDespesas(SQLModel, table=True):
    __tablename__ = "fato_despesas"

    id_orgao_publico: int = Field(foreign_key="dim_orgao_public.id_orgao_publico", primary_key=True)

    valor_empenhado: Optional[Decimal] = None
    valor_pago: Optional[Decimal] = None
    valor_restos_inscritos: Optional[Decimal] = None
    valor_restos_pagos: Optional[Decimal] = None

class DespesaDetalhada(SQLModel):
    id_orgao: int
    nome_orgao: str | None
    valor_pago: Decimal | None
    valor_empenhado: Decimal | None

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI(title="GovSpend Analytics API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/despesas/", response_model=List[DespesaDetalhada])
def list_despesas(session: Session = Depends(get_session)):
    """
    Retorna lista de despesas fazendo JOIN entre Fato e Dimensão.
    """
    statement = select(FatoDespesas, DimOrgaoPublic).join(DimOrgaoPublic)
    results = session.exec(statement).all()

    despesas_formatadas = []
    for fato, dim in results:
        despesas_formatadas.append(
            DespesaDetalhada(
                id_orgao=fato.id_orgao_publico,
                nome_orgao=dim.nome_orgao_subordinado,
                valor_pago=fato.valor_pago,
                valor_empenhado=fato.valor_empenhado
            )
        )
    return despesas_formatadas

@app.get("/despesas/{id_orgao}", response_model=DespesaDetalhada)
def get_despesa(id_orgao: int, session: Session = Depends(get_session)):
    """
    Retorna uma despesa específica pelo ID do Órgão.
    """
    statement = select(FatoDespesas, DimOrgaoPublic).where(
        FatoDespesas.id_orgao_publico == id_orgao
    ).join(DimOrgaoPublic)

    result = session.exec(statement).first()

    if not result:
        raise HTTPException(status_code=404, detail="Despesa/Órgão não encontrado")
    
    fato, dim = result
    return DespesaDetalhada(
        id_orgao=fato.id_orgao_publico,
        nome_orgao=dim.nome_orgao_subordinado,
        valor_pago=fato.valor_pago,
        valor_empenhado=fato.valor_empenhado
    )