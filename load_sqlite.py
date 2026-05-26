from __future__ import annotations

import importlib.util
import sys
import unicodedata
from pathlib import Path

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

BASE_DIR = Path(__file__).resolve().parent
MODELS_PATH = BASE_DIR / "01_models.py"

spec = importlib.util.spec_from_file_location("models", MODELS_PATH)
models = importlib.util.module_from_spec(spec)
if spec is None or spec.loader is None:
	raise RuntimeError("No se pudo cargar 01_models.py")
sys.modules["models"] = models
spec.loader.exec_module(models)

Continente = models.Continente
Pais = models.Pais
Jugador = models.Jugador
create_tables = models.create_tables
get_engine = models.get_engine


def build_country_continent_map() -> dict[str, str]:
	return {
		"Alemania": "Europa",
		"Argentina": "America",
		"Australia": "Oceania",
		"Brasil": "America",
		"Ecuador": "America",
		"Espana": "Europa",
		"Estados Unidos": "America",
		"Francia": "Europa",
		"Inglaterra": "Europa",
		"Japon": "Asia",
		"Marruecos": "Africa",
		"Mexico": "America",
		"Nigeria": "Africa",
		"Portugal": "Europa",
		"Senegal": "Africa",
	}


def normalize_country(name: str) -> str:
	normalized = unicodedata.normalize("NFKD", name)
	normalized = "".join(ch for ch in normalized if not unicodedata.combining(ch))
	return normalized.strip()


def normalize_continent(name: str) -> str:
	return name.strip()


def get_or_create_continent(session: Session, nombre: str) -> Continente:
	stmt = select(Continente).where(Continente.nombre == nombre)
	continente = session.execute(stmt).scalar_one_or_none()
	if continente is None:
		continente = Continente(nombre=nombre)
		session.add(continente)
		session.flush()
	return continente


def get_or_create_country(session: Session, nombre: str, continente: Continente) -> Pais:
	stmt = select(Pais).where(Pais.nombre == nombre)
	pais = session.execute(stmt).scalar_one_or_none()
	if pais is None:
		pais = Pais(nombre=nombre, continente=continente)
		session.add(pais)
		session.flush()
	return pais


def load_sqlite(csv_path: Path, sqlite_path: str = "paises.db") -> None:
	create_tables(sqlite_path)
	engine = get_engine(sqlite_path)

	df = pd.read_csv(csv_path)
	df = df.fillna(0)

	country_map = build_country_continent_map()

	countries_in_file = set(df["pais_nacimiento"].dropna()) | set(
		df["pais_donde_juega"].dropna()
	)
	missing = sorted(
		{
			normalize_country(c)
			for c in countries_in_file
			if normalize_country(c) not in country_map
		}
	)
	if missing:
		raise ValueError(
			"Faltan paises en el mapeo pais->continente: " + ", ".join(missing)
		)

	with Session(engine) as session:
		for _, row in df.iterrows():
			pais_nacimiento_nombre = normalize_country(row["pais_nacimiento"])
			pais_donde_juega_nombre = normalize_country(row["pais_donde_juega"])

			continente_nacimiento = get_or_create_continent(
				session,
				normalize_continent(country_map[pais_nacimiento_nombre]),
			)
			continente_juega = get_or_create_continent(
				session,
				normalize_continent(country_map[pais_donde_juega_nombre]),
			)

			pais_nacimiento = get_or_create_country(
				session, pais_nacimiento_nombre, continente_nacimiento
			)
			pais_donde_juega = get_or_create_country(
				session, pais_donde_juega_nombre, continente_juega
			)

			jugador = Jugador(
				nombre=row["nombre_jugador"],
				pais_nacimiento=pais_nacimiento,
				pais_donde_juega=pais_donde_juega,
				posicion=row["posicion"],
				edad=int(row["edad"]),
				numero_partidos_seleccion=int(row["numero_partidos_seleccion"]),
				goles_seleccion=int(row["goles_seleccion"]),
			)
			session.add(jugador)

		session.commit()


if __name__ == "__main__":
	csv_path = BASE_DIR / "data" / "jugadores_futbol.csv"
	load_sqlite(csv_path)
