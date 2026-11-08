# Sistema de Gestión de Turnos para Trámites de Documentación (RENAPER)

**Trabajo Práctico Integrador (TPI) — Metodología de Sistemas II**  
**Tecnicatura Universitaria en Programación a Distancia (TUPaD) — UTN**

---

## 1. Descripción del Proyecto

Este repositorio contiene la evolución técnica de un sistema de gestión de turnos ciudadanos por consola (inspirado en la operatoria del RENAPER), desarrollado en **Python 3.11** utilizando exclusivamente su biblioteca estándar y persistencia local en archivo JSON (`datos_renaper.json`).

El objetivo central del proyecto no consiste en acumular funcionalidades nuevas, sino en diagnosticar los problemas de **calidad interna, deuda técnica y code smells** presentes en la versión monolítica original (`sistema_inicial.py`, identificada bajo el tag `estado-inicial`) y ejecutar un proceso de **refactoring seguro** aplicando los principios **SOLID** y prácticas de **Clean Code** hasta alcanzar una arquitectura desacoplada de cuatro capas (`estadorefactorizado`), respaldada por una suite automatizada de pruebas unitarias, de persistencia y de equivalencia de extremo a extremo.

### Integrantes del Equipo
* **David Emanuel Vergara:** Relevamiento del sistema base, análisis de calidad externa/interna, diagnóstico de code smells (Etapas 1 a 3) y refactorización de la capa de dominio (`dominio.py`).
* **Mateo Roman Salas:** Diagnóstico de deuda técnica, aplicación de principios SOLID/Clean Code, ejecución de refactorings seguros (Etapas 3 a 5), capas de persistencia (`repositorio.py`) y casos de uso (`servicio.py`).
* **Victor Manuel Barroeta:** Capa de presentación (`cli.py` y `main.py`), estrategia de pruebas y verificación V&V (`tests/`), auditoría de Code Review profesional, conclusiones, mejoras futuras y documentación técnica (`docs/` y `README.md`, Etapas 6 a 8).

---

## 2. Funcionalidades del Sistema

El sistema administra el ciclo de vida de los turnos en tres sedes operativas (`CENTRO`, `NORTE`, `SUR`) para tres prestaciones (`DNI`, `PASAPORTE`, `PARTIDA DE NACIMIENTO`) en modalidad Regular o Exprés/Urgente:

1. **Registrar turno de documentación:** Valida los datos del ciudadano (nombre no vacío, DNI de 7 u 8 caracteres, edad entre 1 y 119 años y trámite válido), calcula automáticamente el arancel según la tabla tarifaria oficial, persiste el registro de forma atómica en `datos_renaper.json` y emite el comprobante en consola.
2. **Cambiar estado y asignar operador:** Localiza un turno por su ID, verifica que el nuevo estado pertenezca al catálogo válido (`PENDIENTE`, `ATENDIDO`, `CANCELADO`), asigna el operador responsable y actualiza la persistencia.
3. **Buscar y filtrar turnos:** Recupera y lista turnos aplicando filtros por `DNI`, `ESTADO` o `SEDE`.
4. **Generar reporte general y de recaudación:** Contabiliza el total de turnos desglosados por estado y calcula la recaudación activa sumando los aranceles de los turnos cobrables (`PENDIENTE` y `ATENDIDO`), excluyendo los `CANCELADO`.

---

## 3. Arquitectura y Estructura del Repositorio

Tras la refactorización (aplicando SRP, OCP y DIP), el monolito inicial fue reemplazado por una arquitectura en cuatro capas con dependencias unidireccionales orientadas hacia el dominio:

```text
TPI_METODOLOGIA_II/
├── README.md                        # Documentación general, instalación y uso
├── main.py                          # Punto de entrada: inyecta dependencias y lanza la CLI
├── cli.py                           # Capa de presentación: única que utiliza input() y print()
├── servicio.py                      # Capa de aplicación/casos de uso (ServicioTurnos, Reporte)
├── dominio.py                       # Capa de dominio pura: entidades, constantes, TARIFAS y validaciones
├── repositorio.py                   # Capa de persistencia JSON: traducción de claves y guardado atómico
├── docs/
│   ├── diagnostico.md               # Diagnóstico de deuda técnica y catálogo de 11 code smells
│   ├── checklist_code_review.md     # Auditoría de Code Review, observaciones y criterios DoD
│   └── decisiones_tecnicas.md       # Registro de decisiones arquitectónicas (ADRs) y mejoras futuras
└── tests/
    ├── __init__.py
    ├── test_dominio.py              # Pruebas unitarias aisladas de aranceles, OCP y casos de borde
    ├── test_servicio.py             # Pruebas unitarias de casos de uso con RepositorioEnMemoria
    ├── test_repositorio.py          # Pruebas de contrato JSON, ida/vuelta y archivo corrupto
    ├── test_equivalencia.py         # Verificación E2E de no regresión contra sistema_inicial.py
    └── referencia/
        └── sistema_inicial.py       # Copia de referencia del monolito inicial para test de regresión
```

---

## 4. Requisitos e Instalación

* **Lenguaje:** Python 3.11 o superior.
* **Dependencias externas:** Ninguna. El proyecto utiliza exclusivamente módulos de la biblioteca estándar de Python (`dataclasses`, `json`, `os`, `tempfile`, `copy`, `subprocess`, `sys`, `unittest`).

### Clonación del repositorio
```bash
git clone https://github.com/DavidVergara2025/TPI_METODOLOGIA_II.git
cd TPI_METODOLOGIA_II
```

---

## 5. Ejecución del Sistema y de las Pruebas Automatizadas

### Ejecutar la aplicación interactiva por consola
Desde el directorio raíz del proyecto:
```bash
python main.py
```

### Ejecutar la suite completa de pruebas (Verificación y Validación)
Para correr los 16 casos de prueba (unitarios de dominio, unitarios de servicio en memoria, integración de repositorio y equivalencia de caja negra):
```bash
python -m unittest discover -s tests -v
```

### Ejecutar un módulo de prueba específico
```bash
python -m unittest tests/test_dominio.py -v
python -m unittest tests/test_servicio.py -v
python -m unittest tests/test_repositorio.py -v
python -m unittest tests/test_equivalencia.py -v
```

---

## 6. Trazabilidad de Tags y Ramas en Git

El repositorio cuenta con los tags obligatorios exigidos por la cátedra para auditar la comparación antes/después y el avance por etapas:

* `estado-inicial`: Versión base monolítica (`sistema_inicial.py`) con deuda técnica y code smells.
* `etapa-diagnostico`: Incorporación del diagnóstico técnico y catálogo de los 11 code smells (`docs/diagnostico.md`).
* `etapa-refactoring`: Cierre de la separación arquitectónica en 4 capas (`dominio.py`, `repositorio.py`, `servicio.py`, `cli.py` y `main.py`).
* `etapa-pruebas`: Incorporación de la suite automatizada en `tests/` verificando 0 regresiones.
* `etapa-docs`: Incorporación de la auditoría de Code Review y decisiones técnicas en `docs/`.
* `estadorefactorizado` (y alias `estado-refactorizado`): Versión final consolidada del proyecto.

Para inspeccionar cualquier estado histórico:
```bash
git checkout estado-inicial
git checkout estadorefactorizado
```
