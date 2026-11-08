import json
import os

ARCHIVO_DB = "datos_renaper.json"
lista_global_turnos = []

def cargar():
    global lista_global_turnos
    if os.path.exists(ARCHIVO_DB):
        try:
            f = open(ARCHIVO_DB, "r", encoding="utf-8")
            lista_global_turnos = json.load(f)
            f.close()
        except:
            lista_global_turnos = []
    else:
        lista_global_turnos = []

def proc_t(nom, doc, ed, tip, urg, sed, mail):
    cargar()
    if nom != "" and nom is not None:
        if len(doc) >= 7 and len(doc) <= 8:
            if ed > 0 and ed < 120:
                p = 0
                if tip == "DNI":
                    if urg == True:
                        p = 8000
                    else:
                        p = 3000
                elif tip == "PASAPORTE":
                    if urg == True:
                        p = 70000
                    else:
                        p = 35000
                elif tip == "PARTIDA DE NACIMIENTO":
                    if urg == True:
                        p = 4500
                    else:
                        p = 1500
                else:
                    print("Error: Tipo de tramite no existe")
                    return False

                if ed < 1:
                    p = 0

                nuevo_id = len(lista_global_turnos) + 1

                t = {
                    "id": nuevo_id,
                    "n": nom,
                    "d": doc,
                    "e": ed,
                    "tr": tip,
                    "u": urg,
                    "s": sed,
                    "m": mail,
                    "p": p,
                    "est": "PENDIENTE",
                    "op": "SIN ASIGNAR"
                }

                lista_global_turnos.append(t)

                f = open(ARCHIVO_DB, "w", encoding="utf-8")
                json.dump(lista_global_turnos, f, indent=4)
                f.close()

                print("==========================================")
                print("TURNO REGISTRADO EN RENAPER - ID: " + str(nuevo_id))
                print("Ciudadano: " + nom + " (DNI: " + doc + ")")
                print("Tramite: " + tip + " | Costo: $" + str(p))
                print("Enviando mail de confirmacion a: " + mail + "...")
                print("==========================================")
                return True
            else:
                print("Edad invalida")
                return False
        else:
            print("DNI invalido (debe tener 7 u 8 caracteres)")
            return False
    else:
        print("Nombre vacio")
        return False

def cambiar_est_y_op(id_buscar, nuevo_est, nuevo_op):
    cargar()
    encontrado = False
    for i in range(len(lista_global_turnos)):
        if lista_global_turnos[i]["id"] == id_buscar:
            encontrado = True
            if nuevo_est == "PENDIENTE" or nuevo_est == "ATENDIDO" or nuevo_est == "CANCELADO":
                lista_global_turnos[i]["est"] = nuevo_est
                lista_global_turnos[i]["op"] = nuevo_op
                
                f = open(ARCHIVO_DB, "w", encoding="utf-8")
                json.dump(lista_global_turnos, f, indent=4)
                f.close()
                
                print("Turno actualizado correctamente.")
                print("Enviando mail de actualizacion a: " + lista_global_turnos[i]["m"] + "...")
                return True
            else:
                print("Estado no valido.")
                return False
    if encontrado == False:
        print("No se encontro el turno.")
        return False

def buscar_turnos(filtro_tipo, valor):
    cargar()
    res = []
    for i in range(len(lista_global_turnos)):
        t = lista_global_turnos[i]
        if filtro_tipo == "DNI" and t["d"] == valor:
            res.append(t)
        elif filtro_tipo == "ESTADO" and t["est"] == valor:
            res.append(t)
        elif filtro_tipo == "SEDE" and t["s"] == valor:
            res.append(t)

    print(f"--- RESULTADOS ENCONTRADOS ({len(res)}) ---")
    for r in res:
        urg_txt = "EXPRES" if r["u"] == True else "REGULAR"
        print(f"ID:{r['id']} | DNI:{r['d']} | {r['n']} | {r['tr']} ({urg_txt}) | Sede:{r['s']} | Estado:{r['est']} | Op:{r['op']} | ${r['p']}")
    return res

def rep():
    cargar()
    tot_rec = 0
    c_pend = 0
    c_aten = 0
    c_canc = 0

    for i in range(len(lista_global_turnos)):
        t = lista_global_turnos[i]
        if t["est"] == "PENDIENTE":
            c_pend = c_pend + 1
            tot_rec = tot_rec + t["p"]
        elif t["est"] == "ATENDIDO":
            c_aten = c_aten + 1
            tot_rec = tot_rec + t["p"]
        elif t["est"] == "CANCELADO":
            c_canc = c_canc + 1

    print("====== REPORTE RENAPER ======")
    print("Total Turnos: " + str(len(lista_global_turnos)))
    print("Pendientes: " + str(c_pend))
    print("Atendidos: " + str(c_aten))
    print("Cancelados: " + str(c_canc))
    print("Recaudacion activa (Pendientes + Atendidos): $" + str(tot_rec))
    print("=============================")

def menu():
    while True:
        print("\n--- SISTEMA DE TURNOS TIPO RENAPER (v1.0) ---")
        print("1. Registrar turno de documentacion")
        print("2. Cambiar estado / Asignar operador")
        print("3. Buscar turnos (por DNI, Estado o Sede)")
        print("4. Ver reporte general y recaudacion")
        print("5. Salir")
        op = input("Seleccione opcion: ")

        if op == "1":
            nom = input("Nombre completo: ")
            doc = input("DNI (sin puntos): ")
            try:
                ed = int(input("Edad: "))
            except:
                ed = -1
            tip = input("Tipo tramite (DNI / PASAPORTE / PARTIDA DE NACIMIENTO): ").upper()
            u_in = input("¿Es urgente/expres? (S/N): ").upper()
            urg = True if u_in == "S" else False
            sed = input("Sede (CENTRO / NORTE / SUR): ").upper()
            mail = input("Email de contacto: ")
            proc_t(nom, doc, ed, tip, urg, sed, mail)

        elif op == "2":
            try:
                id_b = int(input("ID del turno: "))
            except:
                id_b = -1
            n_est = input("Nuevo estado (PENDIENTE / ATENDIDO / CANCELADO): ").upper()
            n_op = input("Nombre del operador asignado: ")
            cambiar_est_y_op(id_b, n_est, n_op)

        elif op == "3":
            f_tip = input("Filtrar por (DNI / ESTADO / SEDE): ").upper()
            val = input("Valor a buscar: ").upper() if f_tip != "DNI" else input("DNI a buscar: ")
            buscar_turnos(f_tip, val)

        elif op == "4":
            rep()

        elif op == "5":
            print("Saliendo...")
            break
        else:
            print("Opcion incorrecta.")

if __name__ == "__main__":
    menu()