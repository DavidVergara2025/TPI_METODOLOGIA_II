# Diagnóstico de Calidad Externa/Interna, Deuda Técnica y Code Smells

**Proyecto:** Sistema de Gestión de Turnos — RENAPER  
**Versión auditada:** `sistema_inicial.py` (Tag: `estado-inicial`)  
**Etapas del TPI cubiertas:** Etapas 1, 2 y 3  

---

## 1. Contraste entre Calidad Externa y Calidad Interna

| Dimensión | Evaluación en `sistema_inicial.py` | Evidencia Técnica |
| :--- | :--- | :--- |
| **Calidad Externa (Vista del Usuario)** | **Satisfactoria.** El menú por consola guía al operador, calcula tarifas correctas, filtra turnos por DNI/Estado/Sede, emite reportes exactos y persiste entre sesiones. | Ejecución interactiva de las 4 operaciones del menú principal sobre `datos_renaper.json`. |
| **Calidad Interna (Vista de Ingeniería)** | **Deficiente.** Monolito de 202 líneas sin separación de capas, acoplado a una variable global mutable, con excepciones silenciadas que destruyen datos y nula capacidad de prueba unitaria aislada. | `sistema_inicial.py` (líneas 1 a 202). |

---

## 2. Áreas de Deuda Técnica Identificadas

1. **Integridad de datos:** La lectura silencia errores con un `except:` desnudo que vacía la lista en memoria; el posterior guardado sobrescribe el archivo real destruyendo el historial previo.
2. **Diseño y arquitectura:** Ausencia total de separación entre interfaz de usuario (`input`/`print`), lógica de negocio y persistencia en disco (`open`/`json.dump`).
3. **Mantenibilidad y legibilidad:** Tarifas y estados dispersos como literales mágicos, claves abreviadas crípticas en el diccionario (`"n"`, `"d"`, `"tr"`, `"est"`) y bloques de escritura duplicados.
4. **Testabilidad:** Imposibilidad de ejercitar las reglas de cálculo de aranceles o validación sin modificar el archivo físico `datos_renaper.json`.

---

## 3. Catálogo de los 11 Code Smells Diagnosticados

| # | Code Smell / Debilidad Técnica | Ubicación en `sistema_inicial.py` | Prioridad | Impacto y Riesgo en el Mantenimiento |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Manejo silencioso de excepciones con pérdida de datos** | `cargar()`, líneas 14-15; `proc_t()`, líneas 65-67 | **Alta** | Si el JSON está dañado, `except:` asigna `lista_global_turnos = []`. Al registrar un turno nuevo, se sobrescribe el archivo y se pierden todos los turnos previos sin aviso. |
| **2** | **Estado global mutable y recarga en cada operación** | Línea 5 (`lista_global_turnos`), línea 8 (`global`), llamadas a `cargar()` en líneas 20, 87, 111 y 129 | **Alta** | Oculta las dependencias en la firma de las funciones, impide aislar pruebas unitarias y acopla todas las operaciones al ciclo de lectura en disco. |
| **3** | **Método largo con múltiples responsabilidades (Long Method / Violación SRP)** | `proc_t()`, líneas 19-84 (66 líneas, 4 niveles de anidamiento) | **Alta** | Valida entradas, calcula tarifas, genera IDs, escribe en disco e imprime en pantalla. Cualquier cambio menor exige editar la función central del sistema. |
| **4** | **Validación de dominio incompleta** | Línea 22 (longitud de DNI) y línea 92 (cambio de estado) | **Alta** | El DNI solo se controla por longitud (`"ABCDEFG"` es válido) y no se restringen transiciones regresivas de estado (ej. pasar de `ATENDIDO` a `PENDIENTE`). |
| **5** | **Números mágicos en la tabla de aranceles (Magic Numbers / Violación OCP)** | `proc_t()`, líneas 26-39 | **Media** | Los montos (`3000`, `8000`, `35000`, `70000`, `1500`, `4500`) están incrustados en condicionales `if/elif`. Agregar un trámite exige modificar la lógica. |
| **6** | **Cadenas mágicas para estados y tipos de trámite (Magic Strings)** | Líneas 25, 30, 35, 59, 92, 137-143 y 171 | **Media** | Literales como `"PENDIENTE"`, `"ATENDIDO"`, `"CANCELADO"` o `"DNI"` repetidos en múltiples funciones; un error tipográfico produce fallos silenciosos. |
| **7** | **Lista larga de parámetros (Long Parameter List / Data Clumps)** | Firma de `proc_t(nom, doc, ed, tip, urg, sed, mail)`, línea 19, y diccionario en líneas 49-61 | **Media** | Siete parámetros viajan juntos sin una entidad de dominio que los agrupe y dote de semántica explícita. |
| **8** | **Código duplicado (Duplicated Code / Violación DRY)** | Escritura JSON en líneas 65-67 y 96-98; sumatorias en `rep()`, líneas 135-144 | **Media** | El bloque `open` / `json.dump` / `close` está copiado en dos funciones; cambiar el mecanismo de persistencia obliga a editar múltiples puntos. |
| **9** | **Nombres poco descriptivos y claves abreviadas** | `proc_t`, `rep`, variables `nom`, `doc`, `ed`, `p`, `t` y claves JSON `"n"`, `"d"`, `"e"`, `"tr"`, `"u"`, `"s"`, `"m"`, `"p"`, `"est"`, `"op"` (líneas 51-60) | **Media** | Eleva la carga cognitiva al leer el código. Renombrar las claves en el código exige además aislar o migrar el esquema del archivo JSON. |
| **10** | **Mezcla de lógica de dominio y presentación** | `print()` dentro de `proc_t()` (69-74), `cambiar_est_y_op()` (100-101), `buscar_turnos()` (122-125) y `rep()` (146-152) | **Media** | Impide reutilizar las reglas de negocio en otra interfaz (API o GUI) y dificulta las pruebas unitarias directas sobre valores de retorno. |
| **11** | **Código inalcanzable, comparaciones redundantes y valores centinela** | Líneas 44-45 (`if ed < 1: p = 0`), líneas 26, 31, 36, 106 y 124 (`== True` / `== False`), líneas 170 y 182 (centinela `-1` con `except:` desnudo) | **Baja** | El bloque `ed < 1` jamás se ejecuta porque la línea 23 ya filtra `ed > 0`. El `except:` desnudo en el menú captura incluso `KeyboardInterrupt` (`Ctrl+C`). |
