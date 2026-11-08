# Checklist Técnico de Code Review y Auditoría de Calidad

**Proyecto:** Sistema de Gestión de Turnos — RENAPER  
**Versión auditada:** `estadorefactorizado` (`dominio.py`, `repositorio.py`, `servicio.py`, `cli.py`, `main.py`, `tests/`)  
**Etapa del TPI:** Etapa 7 (Code Review Profesional)  

---

## 1. Metodología de Revisión Aplicada

Siguiendo las pautas de gobernanza técnica de la cátedra (**Módulo 3: Verificación y Validación — Definition of Done y Revisión por Pares en Pull Requests**), cada incremento desarrollado en las ramas de características (`feature/*`) fue sometido a una inspección estática y dinámica antes de su fusión en `main`.

Los criterios de evaluación exigieron:
1. Resolución trazable de los 11 code smells detectados en la Etapa 3.
2. Respeto estricto de la arquitectura en 4 capas y de los principios SOLID (SRP, OCP, DIP).
3. Verificación empírica de no regresión mediante la ejecución en verde de los 16 tests automatizados.

---

## 2. Tabla de Checklist Técnico de Code Review

| ID | Categoría | Criterio Técnico Auditado | Estado Inicial (`sistema_inicial.py`) | Estado Refactorizado (Módulos) | Evidencia y Ubicación | Dictamen |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **CR-01** | Arquitectura y SRP | Cada módulo y clase posee una única responsabilidad y un único motivo de cambio. | No cumple. Archivo único monolítico de 202 líneas. | Cumple. Separación en 4 capas: `dominio.py`, `repositorio.py`, `servicio.py` y `cli.py` (+ `main.py`). | `dominio.py` (90 lín.), `repositorio.py` (78 lín.), `servicio.py` (85 lín.), `cli.py` (123 lín.). | **APROBADO** |
| **CR-02** | Diseño SOLID (OCP) | Incorporar un nuevo trámite no requiere modificar la lógica de cálculo ni validación. | No cumple. Escalera de `if/elif` anidados en `proc_t()` (líneas 25-42). | Cumple. Tabla `TARIFAS` indexada por `(tipo_tramite, urgente)` consultada por `calcular_arancel()`. | `dominio.py` (líneas 31-38 y 89-90) y `test_dominio.py` (líneas 34-40). | **APROBADO** |
| **CR-03** | Diseño SOLID (DIP) | El servicio de negocio depende de un contrato de persistencia inyectado por constructor. | No cumple. Llamadas directas a `open(ARCHIVO_DB)` y variable global `lista_global_turnos`. | Cumple. `ServicioTurnos.__init__(self, repositorio)` recibe el colaborador externo desde `main.py`. | `servicio.py` (líneas 31-33), `main.py` (línea 10) y `RepositorioEnMemoria` en `test_servicio.py`. | **APROBADO** |
| **CR-04** | Clean Code y Nombres | Identificadores expresivos y libres de abreviaturas crípticas en la lógica del sistema. | No cumple. Nombres `proc_t`, `rep`, `nom`, `doc`, `ed`, `tip`, `urg`, `sed`, `p`, `t`. | Cumple. Nombres claros: `registrar`, `cambiar_estado`, `generar_reporte`, `SolicitudTurno`, `Turno`. | Todos los módulos; claves cortas JSON confinadas a `_a_registro` y `_desde_registro`. | **APROBADO** |
| **CR-05** | Complejidad y Guardas | Funciones breves (menos de 25 líneas) y anidamiento plano con cláusulas de guarda. | No cumple. `proc_t()` tenía 66 líneas y 4 niveles de `if` anidados. | Cumple. `validar_solicitud()` usa cláusulas de guarda de 1 nivel; función más larga de 22 líneas. | `dominio.py` (líneas 77-86) y `cli.py` (`_opcion_registrar`, líneas 26-47). | **APROBADO** |
| **CR-06** | Manejo de Errores | Ausencia de bloques `except:` desnudos y reemplazo de retornos booleanos por excepciones. | No cumple. Tres `except:` desnudos (líneas 14, 169, 181) y retorno `False` tras `print()`. | Cumple. Se lanzan `ErrorNegocio` y `ErrorPersistencia`; `_leer_entero()` captura solo `ValueError`. | `dominio.py` (línea 41), `repositorio.py` (líneas 13, 62), `cli.py` (líneas 10-14, 38, 57, 122). | **APROBADO** |
| **CR-07** | Integridad de Persistencia | Escritura atómica ante fallos y bloqueo de sobrescritura ante archivo JSON corrupto. | No cumple. `open(..., "w")` directo duplicado y vaciado silencioso ante JSON dañado. | Cumple. Escritura con `tempfile.mkstemp` + `os.replace()` y lanzamiento de `ErrorPersistencia`. | `repositorio.py` (`cargar()` en líneas 55-63 y `guardar()` en líneas 65-78). | **APROBADO** |
| **CR-08** | Higiene y Constantes | Eliminación de código muerto, comparaciones redundantes (`== True`) y literales mágicos. | No cumple. Bloque muerto `if ed < 1: p = 0`, `== True` y strings literales dispersos. | Cumple. Código muerto eliminado, booleanos directos y constantes simbólicas en `dominio.py`. | `dominio.py` (líneas 8-27: `TRAMITE_*`, `ESTADO_*`, `ESTADOS_VALIDOS`, `ESTADOS_COBRABLES`). | **APROBADO** |
| **CR-09** | Validación y Centinelas | Consistencia de reglas de dominio frente al contrato externo y preservación de no regresión. | Incompleto. DNI solo validado por longitud, sin máquina de estados y centinela `-1`. | Cumple con observación. Se mantuvo el contrato externo y el `-1` en `_leer_entero()` para no regresión. | `cli.py` (líneas 10-14), `dominio.py` (líneas 81-82) y `servicio.py` (líneas 58-59). | **APROBADO CON OBS.** |

---

## 3. Observaciones de Revisión y Feedback Técnico Documentado

1. **Conservación deliberada del centinela `-1` en `_leer_entero()` (`cli.py`):**
   * *Observación:* Al revisar `cli.py` (líneas 10 a 14), se observó que `_leer_entero(texto)` devuelve `-1` cuando ocurre un `ValueError`.
   * *Resolución y justificación:* Se corrigió el defecto grave del código original (que usaba `except:` desnudo atrapando incluso interrupciones de sistema), restringiendo la captura exclusivamente a `except ValueError:`. Se decidió conservar el valor de retorno `-1` en la frontera de la CLI para que el dato sea rechazado por `validar_solicitud()` o `cambiar_estado()` emitiendo exactamente los mensajes `"Edad invalida"` y `"No se encontro el turno."`, garantizando 100% de compatibilidad en `test_equivalencia.py`.

2. **Diferimiento de validación numérica de DNI y máquina de estados (Hallazgo 4):**
   * *Observación:* `validar_solicitud()` continúa validando el DNI solo por longitud (7 u 8 caracteres) y `cambiar_estado()` permite cualquier transición dentro de `ESTADOS_VALIDOS`.
   * *Resolución y justificación:* Modificar estas dos reglas durante el refactoring habría alterado el comportamiento externo observable (calidad externa) frente a las entradas de prueba de la versión base. El logro arquitectónico de esta entrega consiste en haber extraído y aislado ambas reglas en `dominio.py` y `servicio.py`; su endurecimiento funcional se registra como mejora evolutiva en `docs/decisiones_tecnicas.md`.

---

## 4. Verificación de Definition of Done (DoD) y Criterios de Aceptación

* **[x] Compilación y ejecución limpia:** Ejecución sin errores ni advertencias en Python 3.11 usando solo la biblioteca estándar.
* **[x] Suite de pruebas 100% en verde:** 16 tests ejecutados (`python -m unittest discover -s tests -v`) con resultado `OK`.
* **[x] Equivalencia funcional certificada:** Salida por consola (`stdout`) y contenido de `datos_renaper.json` idénticos entre `sistema_inicial.py` y `main.py` en los 4 escenarios de `test_equivalencia.py`.
* **[x] Protección contra pérdida de datos:** Comprobada mediante `test_archivo_corrupto_no_se_sobrescribe`.
