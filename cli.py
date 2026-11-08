"""Capa de presentación: única que usa input() y print().

Toda la lógica de negocio está en servicio.py y dominio.py. Acá solo se
captura lo que escribe el usuario, se llama al servicio y se muestra el resultado.
"""
from dominio import ErrorNegocio, FILTRO_DNI, FILTRO_ESTADO, FILTRO_SEDE, SolicitudTurno
from repositorio import ErrorPersistencia


def _leer_entero(texto):
    try:
        return int(texto)
    except ValueError:
        return -1


def _mostrar_menu():
    print("\n--- SISTEMA DE TURNOS TIPO RENAPER (v1.0) ---")
    print("1. Registrar turno de documentacion")
    print("2. Cambiar estado / Asignar operador")
    print("3. Buscar turnos (por DNI, Estado o Sede)")
    print("4. Ver reporte general y recaudacion")
    print("5. Salir")


def _opcion_registrar(servicio):
    nombre = input("Nombre completo: ")
    dni = input("DNI (sin puntos): ")
    edad = _leer_entero(input("Edad: "))
    tipo = input("Tipo tramite (DNI / PASAPORTE / PARTIDA DE NACIMIENTO): ").upper()
    urgente = input("¿Es urgente/expres? (S/N): ").upper() == "S"
    sede = input("Sede (CENTRO / NORTE / SUR): ").upper()
    email = input("Email de contacto: ")

    solicitud = SolicitudTurno(nombre, dni, edad, tipo, urgente, sede, email)
    try:
        turno = servicio.registrar(solicitud)
    except ErrorNegocio as error:
        print(error.mensaje)
        return

    print("==========================================")
    print("TURNO REGISTRADO EN RENAPER - ID: " + str(turno.id))
    print("Ciudadano: " + turno.nombre + " (DNI: " + turno.dni + ")")
    print("Tramite: " + turno.tipo_tramite + " | Costo: $" + str(turno.arancel))
    print("Enviando mail de confirmacion a: " + turno.email + "...")
    print("==========================================")


def _opcion_cambiar_estado(servicio):
    id_turno = _leer_entero(input("ID del turno: "))
    nuevo_estado = input("Nuevo estado (PENDIENTE / ATENDIDO / CANCELADO): ").upper()
    operador = input("Nombre del operador asignado: ")

    try:
        turno = servicio.cambiar_estado(id_turno, nuevo_estado, operador)
    except ErrorNegocio as error:
        print(error.mensaje)
        return

    print("Turno actualizado correctamente.")
    print("Enviando mail de actualizacion a: " + turno.email + "...")


def _buscar_segun_filtro(servicio, filtro, valor):
    if filtro == FILTRO_DNI:
        return servicio.buscar_por_dni(valor)
    if filtro == FILTRO_ESTADO:
        return servicio.buscar_por_estado(valor)
    if filtro == FILTRO_SEDE:
        return servicio.buscar_por_sede(valor)
    return []


def _opcion_buscar(servicio):
    filtro = input("Filtrar por (DNI / ESTADO / SEDE): ").upper()
    if filtro != FILTRO_DNI:
        valor = input("Valor a buscar: ").upper()
    else:
        valor = input("DNI a buscar: ")

    turnos = _buscar_segun_filtro(servicio, filtro, valor)
    print(f"--- RESULTADOS ENCONTRADOS ({len(turnos)}) ---")
    for turno in turnos:
        modalidad = "EXPRES" if turno.urgente else "REGULAR"
        print(
            f"ID:{turno.id} | DNI:{turno.dni} | {turno.nombre} | "
            f"{turno.tipo_tramite} ({modalidad}) | Sede:{turno.sede} | "
            f"Estado:{turno.estado} | Op:{turno.operador} | ${turno.arancel}"
        )


def _opcion_reporte(servicio):
    reporte = servicio.generar_reporte()
    print("====== REPORTE RENAPER ======")
    print("Total Turnos: " + str(reporte.total))
    print("Pendientes: " + str(reporte.pendientes))
    print("Atendidos: " + str(reporte.atendidos))
    print("Cancelados: " + str(reporte.cancelados))
    print("Recaudacion activa (Pendientes + Atendidos): $" + str(reporte.recaudacion))
    print("=============================")


def menu(servicio):
    while True:
        _mostrar_menu()
        opcion = input("Seleccione opcion: ")
        try:
            if opcion == "1":
                _opcion_registrar(servicio)
            elif opcion == "2":
                _opcion_cambiar_estado(servicio)
            elif opcion == "3":
                _opcion_buscar(servicio)
            elif opcion == "4":
                _opcion_reporte(servicio)
            elif opcion == "5":
                print("Saliendo...")
                break
            else:
                print("Opcion incorrecta.")
        except ErrorPersistencia as error:
            print(f"ERROR DE DATOS: {error}")
