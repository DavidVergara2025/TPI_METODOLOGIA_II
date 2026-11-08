"""Reglas de negocio del sistema de turnos.

Este módulo no hace entrada/salida: no lee archivos, no usa input() ni print().
Por eso puede probarse de forma aislada.
"""
from dataclasses import dataclass

TRAMITE_DNI = "DNI"
TRAMITE_PASAPORTE = "PASAPORTE"
TRAMITE_PARTIDA = "PARTIDA DE NACIMIENTO"

ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_ATENDIDO = "ATENDIDO"
ESTADO_CANCELADO = "CANCELADO"
ESTADOS_VALIDOS = (ESTADO_PENDIENTE, ESTADO_ATENDIDO, ESTADO_CANCELADO)
ESTADOS_COBRABLES = (ESTADO_PENDIENTE, ESTADO_ATENDIDO)

OPERADOR_SIN_ASIGNAR = "SIN ASIGNAR"

FILTRO_DNI = "DNI"
FILTRO_ESTADO = "ESTADO"
FILTRO_SEDE = "SEDE"

LONGITUD_DNI_MINIMA = 7
LONGITUD_DNI_MAXIMA = 8
EDAD_MINIMA = 1
EDAD_MAXIMA = 119

# Tabla de aranceles: (tipo de trámite, urgente) -> precio en pesos.
# Para agregar un trámite nuevo basta con agregar una entrada aquí (OCP).
TARIFAS = {
    (TRAMITE_DNI, False): 3000,
    (TRAMITE_DNI, True): 8000,
    (TRAMITE_PASAPORTE, False): 35000,
    (TRAMITE_PASAPORTE, True): 70000,
    (TRAMITE_PARTIDA, False): 1500,
    (TRAMITE_PARTIDA, True): 4500,
}


class ErrorNegocio(Exception):
    """Regla de negocio incumplida. El mensaje es el que se muestra al usuario."""

    def __init__(self, mensaje):
        super().__init__(mensaje)
        self.mensaje = mensaje


@dataclass
class SolicitudTurno:
    """Parameter Object: agrupa los datos de una solicitud de trámite."""

    nombre: str
    dni: str
    edad: int
    tipo_tramite: str
    urgente: bool
    sede: str
    email: str


@dataclass
class Turno:
    id: int
    nombre: str
    dni: str
    edad: int
    tipo_tramite: str
    urgente: bool
    sede: str
    email: str
    arancel: int
    estado: str = ESTADO_PENDIENTE
    operador: str = OPERADOR_SIN_ASIGNAR


def validar_solicitud(solicitud):
    """Cláusulas de guarda: cada regla corta la ejecución con su mensaje."""
    if solicitud.nombre is None or solicitud.nombre == "":
        raise ErrorNegocio("Nombre vacio")
    if not LONGITUD_DNI_MINIMA <= len(solicitud.dni) <= LONGITUD_DNI_MAXIMA:
        raise ErrorNegocio("DNI invalido (debe tener 7 u 8 caracteres)")
    if not EDAD_MINIMA <= solicitud.edad <= EDAD_MAXIMA:
        raise ErrorNegocio("Edad invalida")
    if (solicitud.tipo_tramite, solicitud.urgente) not in TARIFAS:
        raise ErrorNegocio("Error: Tipo de tramite no existe")


def calcular_arancel(tipo_tramite, urgente):
    return TARIFAS[(tipo_tramite, urgente)]
