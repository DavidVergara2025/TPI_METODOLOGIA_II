"""Pruebas unitarias de las reglas de negocio (sin archivos ni consola)."""
import unittest
from unittest import mock

from dominio import (
    TARIFAS,
    ErrorNegocio,
    SolicitudTurno,
    calcular_arancel,
    validar_solicitud,
)


def solicitud(**cambios):
    datos = dict(
        nombre="Juan Perez", dni="12345678", edad=30, tipo_tramite="DNI",
        urgente=False, sede="CENTRO", email="juan@mail.com",
    )
    datos.update(cambios)
    return SolicitudTurno(**datos)


class TestAranceles(unittest.TestCase):
    def test_tarifas_por_tipo_y_urgencia(self):
        casos = [
            ("DNI", False, 3000), ("DNI", True, 8000),
            ("PASAPORTE", False, 35000), ("PASAPORTE", True, 70000),
            ("PARTIDA DE NACIMIENTO", False, 1500), ("PARTIDA DE NACIMIENTO", True, 4500),
        ]
        for tipo, urgente, esperado in casos:
            with self.subTest(tipo=tipo, urgente=urgente):
                self.assertEqual(calcular_arancel(tipo, urgente), esperado)

    def test_agregar_tramite_nuevo_no_requiere_tocar_la_logica(self):
        # Demostración de OCP: se agrega una entrada a la tabla y el cálculo funciona.
        tabla_extendida = dict(TARIFAS)
        tabla_extendida[("CERTIFICADO DE DOMICILIO", False)] = 2000
        with mock.patch.dict("dominio.TARIFAS", tabla_extendida, clear=True):
            self.assertEqual(calcular_arancel("CERTIFICADO DE DOMICILIO", False), 2000)
            validar_solicitud(solicitud(tipo_tramite="CERTIFICADO DE DOMICILIO"))


class TestValidaciones(unittest.TestCase):
    def assertRechaza(self, mensaje, **cambios):
        with self.assertRaises(ErrorNegocio) as contexto:
            validar_solicitud(solicitud(**cambios))
        self.assertEqual(contexto.exception.mensaje, mensaje)

    def test_solicitud_valida_no_lanza_error(self):
        validar_solicitud(solicitud())

    def test_nombre_vacio(self):
        self.assertRechaza("Nombre vacio", nombre="")

    def test_dni_longitud(self):
        self.assertRechaza("DNI invalido (debe tener 7 u 8 caracteres)", dni="123456")
        self.assertRechaza("DNI invalido (debe tener 7 u 8 caracteres)", dni="123456789")
        validar_solicitud(solicitud(dni="1234567"))
        validar_solicitud(solicitud(dni="12345678"))

    def test_edad_limites(self):
        self.assertRechaza("Edad invalida", edad=0)
        self.assertRechaza("Edad invalida", edad=120)
        validar_solicitud(solicitud(edad=1))
        validar_solicitud(solicitud(edad=119))

    def test_tipo_inexistente(self):
        self.assertRechaza("Error: Tipo de tramite no existe", tipo_tramite="CERTIFICADO")


if __name__ == "__main__":
    unittest.main()
