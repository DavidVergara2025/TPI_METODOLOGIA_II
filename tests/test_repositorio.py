"""Pruebas de persistencia: formato, ida y vuelta, y archivo corrupto."""
import json
import os
import tempfile
import unittest

from dominio import SolicitudTurno
from repositorio import ErrorPersistencia, RepositorioTurnos
from servicio import ServicioTurnos


class TestRepositorioTurnos(unittest.TestCase):
    def setUp(self):
        self.directorio = tempfile.TemporaryDirectory()
        self.ruta = os.path.join(self.directorio.name, "datos_renaper.json")

    def tearDown(self):
        self.directorio.cleanup()

    def test_ida_y_vuelta_conserva_los_datos(self):
        servicio = ServicioTurnos(RepositorioTurnos(self.ruta))
        registrado = servicio.registrar(
            SolicitudTurno("Ana", "12345678", 30, "DNI", True, "NORTE", "a@b.com")
        )
        recuperados = RepositorioTurnos(self.ruta).cargar()
        self.assertEqual(recuperados, [registrado])

    def test_el_archivo_conserva_el_esquema_original(self):
        ServicioTurnos(RepositorioTurnos(self.ruta)).registrar(
            SolicitudTurno("Ana", "12345678", 30, "DNI", False, "CENTRO", "a@b.com")
        )
        with open(self.ruta, encoding="utf-8") as archivo:
            registro = json.load(archivo)[0]
        self.assertEqual(set(registro), {"id", "n", "d", "e", "tr", "u", "s", "m", "p", "est", "op"})

    def test_archivo_corrupto_no_se_sobrescribe(self):
        # Cambio deliberado frente a la versión inicial, que reemplazaba los
        # datos por una lista vacía y perdía todos los turnos.
        contenido_danado = "{esto no es json"
        with open(self.ruta, "w", encoding="utf-8") as archivo:
            archivo.write(contenido_danado)
        servicio = ServicioTurnos(RepositorioTurnos(self.ruta))
        with self.assertRaises(ErrorPersistencia):
            servicio.registrar(
                SolicitudTurno("Ana", "12345678", 30, "DNI", False, "CENTRO", "a@b.com")
            )
        with open(self.ruta, encoding="utf-8") as archivo:
            self.assertEqual(archivo.read(), contenido_danado)


if __name__ == "__main__":
    unittest.main()
