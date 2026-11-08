"""Punto de entrada. Arma las dependencias y lanza el menú."""
from cli import menu
from repositorio import RepositorioTurnos
from servicio import ServicioTurnos

ARCHIVO_DB = "datos_renaper.json"


def main():
    servicio = ServicioTurnos(RepositorioTurnos(ARCHIVO_DB))
    menu(servicio)


if __name__ == "__main__":
    main()
