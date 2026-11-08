"""Persistencia en archivo JSON.

Es el único módulo que conoce el formato del archivo. Si mañana se cambia
a SQLite u otro almacenamiento, solo cambia este módulo.
"""
import json
import os
import tempfile

from dominio import Turno


class ErrorPersistencia(Exception):
    """El archivo de datos existe pero no puede leerse. No se sobrescribe."""


# El archivo conserva el esquema original (claves abreviadas) para no invalidar
# datos ya guardados. La traducción entre el esquema y el objeto Turno vive solo aquí.
def _a_registro(turno):
    return {
        "id": turno.id,
        "n": turno.nombre,
        "d": turno.dni,
        "e": turno.edad,
        "tr": turno.tipo_tramite,
        "u": turno.urgente,
        "s": turno.sede,
        "m": turno.email,
        "p": turno.arancel,
        "est": turno.estado,
        "op": turno.operador,
    }


def _desde_registro(registro):
    return Turno(
        id=registro["id"],
        nombre=registro["n"],
        dni=registro["d"],
        edad=registro["e"],
        tipo_tramite=registro["tr"],
        urgente=registro["u"],
        sede=registro["s"],
        email=registro["m"],
        arancel=registro["p"],
        estado=registro["est"],
        operador=registro["op"],
    )


class RepositorioTurnos:
    def __init__(self, ruta):
        self._ruta = ruta

    def cargar(self):
        if not os.path.exists(self._ruta):
            return []
        try:
            with open(self._ruta, "r", encoding="utf-8") as archivo:
                registros = json.load(archivo)
            return [_desde_registro(registro) for registro in registros]
        except (OSError, ValueError, KeyError, TypeError) as error:
            raise ErrorPersistencia(f"No se pudo leer {self._ruta}: {error}") from error

    def guardar(self, turnos):
        """Escritura atómica: se escribe en un temporal y luego se reemplaza.
        Si la escritura falla, el archivo original queda intacto."""
        registros = [_a_registro(turno) for turno in turnos]
        directorio = os.path.dirname(os.path.abspath(self._ruta))
        descriptor, temporal = tempfile.mkstemp(dir=directorio, suffix=".tmp")
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8") as archivo:
                json.dump(registros, archivo, indent=4)
            os.replace(temporal, self._ruta)
        except BaseException:
            if os.path.exists(temporal):
                os.remove(temporal)
            raise
