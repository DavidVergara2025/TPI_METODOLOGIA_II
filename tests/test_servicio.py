"""Pruebas del servicio con un repositorio en memoria (sin tocar el disco)."""
import copy
import unittest

from dominio import ErrorNegocio, SolicitudTurno, ESTADO_CANCELADO, ESTADO_ATENDIDO
from servicio import ServicioTurnos


class RepositorioEnMemoria:
    def __init__(self):
        self.turnos = []

    def cargar(self):
        return copy.deepcopy(self.turnos)

    def guardar(self, turnos):
        self.turnos = copy.deepcopy(turnos)


def solicitud(dni="12345678", tipo="DNI", urgente=False, sede="CENTRO"):
    return SolicitudTurno("Ana", dni, 30, tipo, urgente, sede, "ana@mail.com")


class TestServicioTurnos(unittest.TestCase):
    def setUp(self):
        self.repo = RepositorioEnMemoria()
        self.servicio = ServicioTurnos(self.repo)

    def test_registrar_asigna_id_secuencial_y_arancel(self):
        primero = self.servicio.registrar(solicitud())
        segundo = self.servicio.registrar(solicitud(tipo="PASAPORTE", urgente=True))
        self.assertEqual((primero.id, segundo.id), (1, 2))
        self.assertEqual(segundo.arancel, 70000)
        self.assertEqual(len(self.repo.turnos), 2)

    def test_cambiar_estado_inexistente(self):
        with self.assertRaises(ErrorNegocio) as ctx:
            self.servicio.cambiar_estado(99, ESTADO_ATENDIDO, "Pedro")
        self.assertEqual(ctx.exception.mensaje, "No se encontro el turno.")

    def test_cambiar_estado_invalido_no_modifica_el_turno(self):
        self.servicio.registrar(solicitud())
        with self.assertRaises(ErrorNegocio) as ctx:
            self.servicio.cambiar_estado(1, "RARO", "Pedro")
        self.assertEqual(ctx.exception.mensaje, "Estado no valido.")
        self.assertEqual(self.repo.turnos[0].estado, "PENDIENTE")

    def test_buscar_por_dni(self):
        self.servicio.registrar(solicitud(dni="11111111"))
        self.servicio.registrar(solicitud(dni="22222222"))
        encontrados = self.servicio.buscar_por_dni("11111111")
        self.assertEqual([t.id for t in encontrados], [1])

    def test_reporte_excluye_cancelados_de_la_recaudacion(self):
        self.servicio.registrar(solicitud(tipo="DNI"))                    # 3000
        self.servicio.registrar(solicitud(tipo="PASAPORTE"))              # 35000
        self.servicio.cambiar_estado(2, ESTADO_CANCELADO, "Pedro")
        reporte = self.servicio.generar_reporte()
        self.assertEqual(reporte.total, 2)
        self.assertEqual(reporte.cancelados, 1)
        self.assertEqual(reporte.recaudacion, 3000)


if __name__ == "__main__":
    unittest.main()
