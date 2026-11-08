# Registro de Decisiones Técnicas (ADR) y Plan de Evolución

**Proyecto:** Sistema de Gestión de Turnos — RENAPER  
**Etapas del TPI:** Etapas 4, 5, 7 y 8  

---

## 1. Decisiones Arquitectónicas Tomadas durante el Refactoring

### Decisión 1: Separación en 4 capas sin dependencias externas
* **Contexto:** En `sistema_inicial.py`, la lectura de teclado, las reglas de aranceles, el estado global `lista_global_turnos` y la escritura en disco convivían en las mismas funciones.
* **Decisión:** Dividir el sistema en cuatro módulos con responsabilidades únicas (SRP) y dependencias orientadas hacia el dominio: `cli.py` -> `servicio.py` -> (`dominio.py`, `repositorio.py`).
* **Consecuencia:** `dominio.py` no importa `os`, `json` ni usa `input()`/`print()`, permitiendo probar toda la lógica de negocio en memoria en milisegundos.

### Decisión 2: Tabla de búsqueda `TARIFAS` en lugar de polimorfismo de clases para OCP
* **Contexto:** El cálculo de aranceles original utilizaba condicionales `if/elif` anidados por tipo de trámite y urgencia.
* **Alternativas evaluadas:** Crear una jerarquía polimórfica de clases (`TramiteDNI`, `TramitePasaporte`, `TramitePartida`) vs. definir un diccionario declarativo `TARIFAS` indexado por la tupla `(tipo_tramite, urgente)`.
* **Decisión:** Se optó por la tabla `TARIFAS` en `dominio.py` porque la regla de negocio actual es una asignación directa de precio sin algoritmos diferentes por trámite.
* **Consecuencia:** Cumple el Principio de Abierto/Cerrado (demostrado en `test_agregar_tramite_nuevo_no_requiere_tocar_la_logica` con `"CERTIFICADO DE DOMICILIO"`) evitando sobre-ingeniería innecesaria (KISS/YAGNI).

### Decisión 3: Traducción de claves abreviadas JSON en `repositorio.py` (`_a_registro` y `_desde_registro`)
* **Contexto:** El archivo `datos_renaper.json` generado por la versión inicial utiliza claves crípticas de una o dos letras (`"n"`, `"d"`, `"e"`, `"tr"`, `"u"`, `"s"`, `"m"`, `"p"`, `"est"`, `"op"`).
* **Decisión:** Mantener intacto el formato del archivo JSON para no invalidar datos ya persistidos ni romper las pruebas de equivalencia contra la versión inicial, concentrando el mapeo hacia/desde atributos expresivos de la dataclass `Turno` exclusivamente en las funciones privadas `_a_registro()` y `_desde_registro()` de `repositorio.py`.
* **Consecuencia:** El resto del sistema trabaja con nombres limpios (`turno.nombre`, `turno.dni`, `turno.tipo_tramite`, `turno.arancel`) mientras el almacenamiento conserva 100% de retrocompatibilidad.

### Decisión 4: Escritura atómica y lanzamiento de `ErrorPersistencia`
* **Contexto:** La versión original abría `datos_renaper.json` con `open(..., "w")` directamente y ante un fallo de lectura vaciaba la lista global sobrescribiendo el archivo.
* **Decisión:** En `RepositorioTurnos.guardar()` se implementó escritura atómica volcando primero a un archivo temporal en el mismo directorio (`tempfile.mkstemp`) y reemplazando el destino mediante `os.replace()`. En `RepositorioTurnos.cargar()`, cualquier error de lectura o parseo lanza `ErrorPersistencia` sin sobrescribir el archivo.
* **Consecuencia:** Se erradica el riesgo de pérdida silenciosa de datos (mejora no regresiva verificada en `test_repositorio.py`).

---

## 2. Hoja de Ruta y Mejoras Futuras Planificadas (Etapa 8)

1. **Script de migración del esquema JSON (Resolución de deuda de claves abreviadas):**
   * Crear la utilidad `scripts/migrar_esquema_json.py` que lea `datos_renaper.json` con claves abreviadas (`"n"`, `"d"`, `"tr"`, etc.), genere un respaldo `.bak`, transforme los registros a claves semánticas completas (`"nombre"`, `"dni"`, `"tipo_tramite"`, `"arancel"`, etc.) mediante escritura atómica y actualice `_a_registro()` / `_desde_registro()` a la versión 2.0 del esquema.
2. **Endurecimiento de validaciones de dominio:**
   * Incorporar `solicitud.dni.isdigit()` en `validar_solicitud()`, validación sintáctica de correo electrónico y validación de sede contra una tupla `SEDES_VALIDAS = ("CENTRO", "NORTE", "SUR")`.
3. **Máquina de estados finitos para transiciones de turnos:**
   * Restringir en `dominio.py` las transiciones válidas para impedir que un turno en estado final (`ATENDIDO` o `CANCELADO`) vuelva a `PENDIENTE`.
4. **Generación de IDs resistente a bajas:**
   * Reemplazar `len(turnos) + 1` por `max((t.id for t in turnos), default=0) + 1`.
5. **Automatización con Pre-commit Hooks y CI/CD:**
   * Configurar ejecución automática de formateador (`black`), linter (`flake8`/`ruff`) y cobertura (`coverage run -m unittest`) en cada commit y Pull Request.
