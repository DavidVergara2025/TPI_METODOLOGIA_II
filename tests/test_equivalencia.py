"""Pruebas de comportamiento externo (etapa 6).

Ejecuta la versión inicial (referencia) y la refactorizada con las mismas
entradas por teclado, en directorios temporales separados, y compara:
  - la salida completa por consola
  - el contenido final del archivo datos_renaper.json
Si ambas coinciden, el refactoring no alteró el comportamiento observable.
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIGINAL = os.path.join(RAIZ, "tests", "referencia", "sistema_inicial.py")
NUEVO = os.path.join(RAIZ, "main.py")
ARCHIVO = "datos_renaper.json"

ESCENARIOS = {
    "flujo_completo": [
        "1", "Juan Perez", "12345678", "30", "dni", "n", "centro", "juan@mail.com",
        "1", "Maria", "7654321", "40", "PASAPORTE", "S", "NORTE", "m@x.com",
        "1", "Ana", "1234567", "5", "PARTIDA DE NACIMIENTO", "N", "sur", "a@x.com",
        "2", "1", "atendido", "Pedro",
        "2", "9", "PENDIENTE", "Luis",
        "2", "2", "estado_raro", "Luis",
        "2", "abc", "PENDIENTE", "x",
        "3", "DNI", "12345678",
        "3", "estado", "pendiente",
        "3", "sede", "norte",
        "3", "otro", "x",
        "4",
        "9",
        "5",
    ],
    "validaciones": [
        "1", "", "12345678", "30", "DNI", "N", "CENTRO", "a@b",
        "1", "X", "123456", "30", "DNI", "N", "CENTRO", "a@b",
        "1", "X", "1234567890", "30", "DNI", "N", "CENTRO", "a@b",
        "1", "X", "12345678", "abc", "DNI", "N", "CENTRO", "a@b",
        "1", "X", "12345678", "0", "DNI", "N", "CENTRO", "a@b",
        "1", "X", "12345678", "120", "DNI", "N", "CENTRO", "a@b",
        "1", "X", "12345678", "119", "DNI", "N", "CENTRO", "a@b",
        "1", "X", "12345678", "30", "CERTIFICADO", "N", "CENTRO", "a@b",
        "4",
        "5",
    ],
    "sin_datos": ["2", "1", "ATENDIDO", "x", "3", "DNI", "1", "4", "5"],
    "opcion_invalida_y_reporte_vacio": ["7", "4", "5"],
}


def _ejecutar(script, entradas, directorio):
    resultado = subprocess.run(
        [sys.executable, script],
        input="\n".join(entradas) + "\n",
        capture_output=True,
        text=True,
        cwd=directorio,
        timeout=20,
    )
    ruta = os.path.join(directorio, ARCHIVO)
    datos = None
    if os.path.exists(ruta):
        with open(ruta, encoding="utf-8") as archivo:
            datos = json.load(archivo)
    return resultado.stdout, datos


class TestEquivalenciaConVersionInicial(unittest.TestCase):
    def test_mismo_comportamiento_en_todos_los_escenarios(self):
        for nombre, entradas in ESCENARIOS.items():
            with self.subTest(escenario=nombre):
                with tempfile.TemporaryDirectory() as dir_original, \
                        tempfile.TemporaryDirectory() as dir_nuevo:
                    salida_original, datos_original = _ejecutar(ORIGINAL, entradas, dir_original)
                    salida_nueva, datos_nuevos = _ejecutar(NUEVO, entradas, dir_nuevo)
                self.assertEqual(salida_nueva, salida_original)
                self.assertEqual(datos_nuevos, datos_original)


if __name__ == "__main__":
    unittest.main()
