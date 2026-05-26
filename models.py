from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
	pass


class Continente(Base):
	__tablename__ = "continentes"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

	paises: Mapped[list["Pais"]] = relationship("Pais", back_populates="continente")


class Pais(Base):
	__tablename__ = "paises"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
	continente_id: Mapped[int] = mapped_column(ForeignKey("continentes.id"), nullable=False)

	continente: Mapped[Continente] = relationship("Continente", back_populates="paises")
	jugadores_nacimiento: Mapped[list["Jugador"]] = relationship(
		"Jugador",
		back_populates="pais_nacimiento",
		foreign_keys="Jugador.pais_nacimiento_id",
	)
	jugadores_club: Mapped[list["Jugador"]] = relationship(
		"Jugador",
		back_populates="pais_donde_juega",
		foreign_keys="Jugador.pais_donde_juega_id",
	)


class Jugador(Base):
	__tablename__ = "jugadores"

	id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
	nombre: Mapped[str] = mapped_column(String(150), nullable=False)
	posicion: Mapped[str] = mapped_column(String(100), nullable=False)
	edad: Mapped[int] = mapped_column(Integer, nullable=False)
	numero_partidos_seleccion: Mapped[int] = mapped_column(Integer, nullable=False)
	goles_seleccion: Mapped[int] = mapped_column(Integer, nullable=False)

	pais_nacimiento_id: Mapped[int] = mapped_column(ForeignKey("paises.id"), nullable=False)
	pais_donde_juega_id: Mapped[int] = mapped_column(ForeignKey("paises.id"), nullable=False)

	pais_nacimiento: Mapped[Pais] = relationship(
		"Pais",
		back_populates="jugadores_nacimiento",
		foreign_keys=[pais_nacimiento_id],
	)
	pais_donde_juega: Mapped[Pais] = relationship(
		"Pais",
		back_populates="jugadores_club",
		foreign_keys=[pais_donde_juega_id],
	)


def get_engine(sqlite_path: str = "paises.db"):
	return create_engine(f"sqlite:///{sqlite_path}", echo=False, future=True)


def create_tables(sqlite_path: str = "paises.db") -> None:
	engine = get_engine(sqlite_path)
	Base.metadata.create_all(engine)


if __name__ == "__main__":
	create_tables()
