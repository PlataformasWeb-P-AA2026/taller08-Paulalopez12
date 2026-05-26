from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "paises.db"

st.set_page_config(page_title="Taller 08 - Jugadores", layout="wide")

st.title("Taller 08 - Integracion de datos")

if not DB_PATH.exists():
    st.error("No se encontro la base de datos paises.db. Ejecuta 02_load_sqlite.py.")
    st.stop()

engine = create_engine(f"sqlite:///{DB_PATH}", future=True)

st.subheader("Tabla 1: Jugadores")
query_jugadores = text(
    """
    SELECT
        j.nombre AS nombre_jugador,
        pn.nombre AS pais_nacimiento,
        pj.nombre AS pais_donde_juega,
        j.posicion,
        j.edad,
        j.numero_partidos_seleccion,
        j.goles_seleccion,
        c.nombre AS continente
    FROM jugadores j
    JOIN paises pn ON pn.id = j.pais_nacimiento_id
    JOIN paises pj ON pj.id = j.pais_donde_juega_id
    JOIN continentes c ON c.id = pn.continente_id
    ORDER BY j.nombre
    """
)
with engine.connect() as conn:
    df_jugadores = pd.read_sql(query_jugadores, conn)

st.dataframe(df_jugadores, use_container_width=True)

st.subheader("Tabla 2: Resumen por continente")
query_continente = text(
    """
    SELECT
        c.nombre AS continente,
        COUNT(j.id) AS numero_jugadores,
        COALESCE(SUM(j.goles_seleccion), 0) AS total_goles
    FROM jugadores j
    JOIN paises pn ON pn.id = j.pais_nacimiento_id
    JOIN continentes c ON c.id = pn.continente_id
    GROUP BY c.nombre
    ORDER BY c.nombre
    """
)
with engine.connect() as conn:
    df_continente = pd.read_sql(query_continente, conn)

st.dataframe(df_continente, use_container_width=True)

st.subheader("Tabla 3: Resumen por pais")
query_pais = text(
    """
    SELECT
        p.nombre AS pais,
        COUNT(j.id) AS numero_jugadores,
        COALESCE(SUM(j.goles_seleccion), 0) AS total_goles
    FROM jugadores j
    JOIN paises p ON p.id = j.pais_nacimiento_id
    GROUP BY p.nombre
    ORDER BY p.nombre
    """
)
with engine.connect() as conn:
    df_pais = pd.read_sql(query_pais, conn)

st.dataframe(df_pais, use_container_width=True)
