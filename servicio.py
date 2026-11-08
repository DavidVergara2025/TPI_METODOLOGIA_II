"""Casos de uso del sistema: orquestan reglas de dominio y persistencia.

El servicio recibe un repositorio por constructor y no conoce el archivo JSON
(Dependency Inversion). Cualquier objeto con cargar() y guardar() sirve,
incluido un repositorio en memoria para pruebas.
"""
from dataclasses import dataclass

from dominio import (
    ESTADO_ATENDIDO,
    ESTADO_CANCELADO,
    ESTADO_PENDIENTE,
    ESTADOS_COBRABLES,
    ESTADOS_VALIDOS,
    ErrorNegocio,
    Turno,
    calcular_arancel,
    validar_solicitud,
)


@dataclass
class Reporte:
    total: int
    pendientes: int
    atendidos: int
    cancelados: int
    recaudacion: int


class ServicioTurnos:
    def __init__(self, repositorio):
        self._repositorio = repositorio

    def registrar(self, solicitud):
        validar_solicitud(solicitud)
        turnos = self._repositorio.cargar()
        turno = Turno(
            id=len(turnos) + 1,
            nombre=solicitud.nombre,
            dni=solicitud.dni,
            edad=solicitud.edad,
            tipo_tramite=solicitud.tipo_tramite,
            urgente=solicitud.urgente,
            sede=solicitud.sede,
            email=solicitud.email,
            arancel=calcular_arancel(solicitud.tipo_tramite, solicitud.urgente),
        )
        turnos.append(turno)
        self._repositorio.guardar(turnos)
        return turno

    def cambiar_estado(self, id_turno, nuevo_estado, operador):
        turnos = self._repositorio.cargar()
        turno = next((t for t in turnos if t.id == id_turno), None)
        if turno is None:
            raise ErrorNegocio("No se encontro el turno.")
        if nuevo_estado not in ESTADOS_VALIDOS:
            raise ErrorNegocio("Estado no valido.")
        turno.estado = nuevo_estado
        turno.operador = operador
        self._repositorio.guardar(turnos)
        return turno

    def buscar_por_dni(self, dni):
        return self._filtrar(lambda t: t.dni == dni)

    def buscar_por_estado(self, estado):
        return self._filtrar(lambda t: t.estado == estado)

    def buscar_por_sede(self, sede):
        return self._filtrar(lambda t: t.sede == sede)

    def _filtrar(self, condicion):
        return [t for t in self._repositorio.cargar() if condicion(t)]

    def generar_reporte(self):
        turnos = self._repositorio.cargar()
        return Reporte(
            total=len(turnos),
            pendientes=sum(1 for t in turnos if t.estado == ESTADO_PENDIENTE),
            atendidos=sum(1 for t in turnos if t.estado == ESTADO_ATENDIDO),
            cancelados=sum(1 for t in turnos if t.estado == ESTADO_CANCELADO),
            recaudacion=sum(t.arancel for t in turnos if t.estado in ESTADOS_COBRABLES),
        )
