DROP TABLE IF EXISTS public.fato_despesas CASCADE;
DROP TABLE IF EXISTS public.dim_orgao_public CASCADE;

CREATE TABLE public.dim_orgao_public (
    id_orgao_publico        INTEGER PRIMARY KEY,
    cod_orgao_superior      TEXT,
    nome_orgao_superior     TEXT,
    cod_orgao_subordinado   TEXT,
    nome_orgao_subordinado  TEXT,
    cod_gestao              TEXT,
    nome_gestao             TEXT
);

CREATE TABLE public.fato_despesas (
    id_orgao_publico        INTEGER NOT NULL,
    valor_empenhado         NUMERIC(18, 2),
    valor_pago              NUMERIC(18, 2),
    valor_restos_inscritos  NUMERIC(18, 2),
    valor_restos_pagos      NUMERIC(18, 2)
);

ALTER TABLE public.fato_despesas
    ADD CONSTRAINT fk_fato_dim_orgao
    FOREIGN KEY (id_orgao_publico)
    REFERENCES public.dim_orgao_public (id_orgao_publico);

CREATE INDEX idx_fato_orgao ON public.fato_despesas(id_orgao_publico);