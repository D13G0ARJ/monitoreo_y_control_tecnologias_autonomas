# Descripción de Módulos

## 1. Objetivo de este documento
Este documento explica qué hace cada archivo o conjunto principal de archivos del sistema.

Su propósito es ayudar a responder preguntas como:

- ¿cómo está organizado el proyecto?
- ¿qué hace cada parte?
- ¿dónde está la lógica principal?
- ¿cómo se separa la interfaz de la simulación?

Este documento es especialmente útil si el jurado pregunta por el desarrollo interno del software.

---

## 2. Estructura general del proyecto

La estructura principal del proyecto es la siguiente:

- `main.py`
- `app/config/`
- `app/domain/`
- `app/services/`
- `app/simulation/`
- `app/io/`
- `app/runtime/`
- `app/ui/`

Cada carpeta cumple una función específica.

---

## 3. Archivo principal

## 3.1 `main.py`

### Qué hace
Es el punto de entrada del sistema.

### Responsabilidades
- iniciar la aplicación;
- crear el motor de simulación;
- abrir las dos ventanas principales;
- conectar la comunicación entre Radar Operativo y Centro de Control.

### Por qué es importante
Porque organiza el arranque general del sistema sin mezclar toda la lógica en un solo lugar.

---

## 4. Carpeta `app/config`

## 4.1 `settings.py`

### Qué hace
Contiene la configuración global del sistema.

### Qué guarda
- tamaños de ventanas;
- nombres de escenarios;
- nombres de modos;
- constantes visuales;
- colores;
- umbrales;
- parámetros por defecto.

### Por qué es importante
Permite cambiar valores globales sin alterar toda la lógica del sistema.

---

## 5. Carpeta `app/domain`

La carpeta `domain` contiene las entidades principales del sistema.

## 5.1 `autonomous_unit.py`

### Qué hace
Define la estructura de una unidad autónoma.

### Qué contiene conceptualmente
- identificador;
- posición;
- velocidad;
- altitud;
- batería;
- estado;
- rol;
- tarea;
- enjambre;
- waypoint;
- ruta;
- trayectoria.
- estado de retorno a base;
- estado de recarga;
- distancia al objetivo.

### Por qué es importante
Porque representa el objeto central del sistema.

## 5.2 `waypoint.py`

### Qué hace
Define la estructura de un waypoint u objetivo.

### Qué representa
Un punto hacia el cual debe moverse una unidad.

## 5.3 `alert.py`

### Qué hace
Define la estructura de una alerta.

### Qué representa
Un evento importante del sistema, con unidad asociada, severidad, hora y descripción.

---

## 6. Carpeta `app/services`

Aquí se concentran servicios especializados. Son módulos que organizan reglas del sistema.

## 6.1 `alert_service.py`

### Qué hace
Evalúa condiciones que deben convertirse en alertas.

### Ejemplos
- batería baja;
- batería crítica;
- sin batería;
- fuera de zona;
- objetivo alcanzado.

### Por qué es importante
Centraliza la lógica de alertas para que no quede dispersa.

## 6.2 `mode_service.py`

### Qué hace
Aplica la lógica de comportamiento según el modo operativo.

### Qué organiza
- patrullaje;
- reconocimiento;
- modo mixto;
- avance de rutas.

## 6.3 `swarm_service.py`

### Qué hace
Organiza las unidades en enjambres operativos.

### Qué resuelve
- asignar `E1` y `E2`;
- definir rol de cada enjambre;
- construir resúmenes de enjambres.

### Por qué es importante
Es el módulo que permite pasar de control individual a gestión grupal.

## 6.4 `scenario_service.py`

### Qué hace
Aplica la configuración de escenarios.

### Qué decide
- cuántas unidades usar;
- cuántos enjambres activar;
- si usar unidades existentes o reemplazar;
- qué parámetros globales aplicar;
- qué escenario queda activo.

### Por qué es importante
Separa la lógica de escenarios del resto de la interfaz.

## 6.5 `battery_service.py`

### Qué hace
Controla la lógica de retorno a base y recarga.

### Qué decide
- cuándo una unidad debe iniciar retorno a base;
- cuándo una unidad llegó a la base;
- cómo se recarga;
- cuándo se restaura la misión anterior.

### Por qué es importante
Permite que el comportamiento de batería sea más realista y no dependa directamente de la interfaz.

## 6.6 `metrics_service.py`

### Qué hace
Acumula métricas de la corrida.

### Qué registra
- distancia recorrida por unidad;
- objetivos alcanzados;
- tiempo al primer objetivo;
- muestras de batería;
- tiempo por estado;
- alertas por tipo y severidad;
- datos de serie temporal para exportación.

### Por qué es importante
Convierte la simulación en evidencia medible para análisis y defensa académica.

---

## 7. Carpeta `app/simulation`

## 7.1 `simulation_engine.py`

### Qué hace
Es el núcleo del sistema.

### Responsabilidades
- almacenar las unidades;
- actualizar la simulación;
- mover las unidades;
- gestionar batería;
- aplicar estados;
- registrar alertas;
- controlar selección;
- iniciar, pausar y reiniciar.
- avanzar la simulación por pasos lógicos;
- integrar unidades nuevas al escenario activo.

### Por qué es importante
Es la pieza central sobre la que trabajan todas las demás.

El método de paso lógico permite que la simulación avance tanto desde el temporizador de la interfaz como desde el modo headless.

## 7.2 `control.py`

### Qué hace
Contiene la lógica de movimiento dirigida hacia objetivos.

### Qué representa
La implementación del control proporcional simple.

### Por qué es importante
Permite traducir un objetivo espacial en desplazamiento controlado.

---

## 8. Carpeta `app/ui`

Aquí están los elementos visibles de la aplicación.

## 8.1 `main_window.py`

### Qué hace
Construye la ventana **Radar Operativo**.

### Qué controla
- integración del radar con el motor;
- actualización visual del radar;
- recepción de selección de unidades.

## 8.2 `control_window.py`

### Qué hace
Construye la ventana **Centro de Control**.

### Qué controla
- pestañas;
- cambio de escenario;
- cambio de modo;
- actualización de paneles;
- respuesta a alertas;
- control de botones principales.

## 8.3 `radar_view.py`

### Qué hace
Dibuja el radar y sus elementos gráficos.

### Qué representa visualmente
- círculos concéntricos;
- barrido radar;
- zona estratégica;
- puntos de observación;
- unidades;
- rutas;
- trayectorias;
- etiquetas;
- HUD.

### Por qué es importante
Es el componente visual más representativo del sistema.

## 8.4 `panels.py`

### Qué hace
Contiene los paneles y pestañas que forman el Centro de Control.

### Qué incluye
- panel de estado global;
- panel de unidad seleccionada;
- panel de enjambres;
- panel de parámetros;
- panel de alertas;
- panel de lista de unidades;
- panel de gráficos;
- controles de simulación.

## 8.5 `scenario_dialog.py`

### Qué hace
Muestra el diálogo **Configurar escenario**.

### Qué permite
- seleccionar cantidad de unidades;
- número de enjambres;
- distribución;
- parámetros operativos;
- usar unidades existentes o reemplazar.

### Por qué es importante
Hace que el escenario sea una decisión confirmada por el operador, no un cambio automático.

---

## 9. Carpeta `app/io`

## 9.1 `exporter.py`

### Qué hace
Exporta informes de simulación.

### Qué genera
- `timeseries.csv`;
- `summary.json`.

### Por qué es importante
Permite conservar resultados de una corrida y usarlos como evidencia técnica.

## 9.2 `scenario_io.py`

### Qué hace
Guarda y carga configuraciones de escenario en JSON.

### Por qué es importante
Permite reutilizar escenarios sin volver a configurarlos manualmente.

---

## 10. Carpeta `app/runtime`

## 10.1 `engine_builder.py`

### Qué hace
Construye un motor de simulación configurado para un escenario.

### Por qué es importante
Centraliza la creación del motor para corridas automáticas.

## 10.2 `headless.py`

### Qué hace
Ejecuta la simulación sin abrir ventanas.

### Qué permite
- corridas deterministas con semilla;
- duración configurable;
- escala de tiempo;
- exportación automática de informes.

### Por qué es importante
Permite usar el sistema como herramienta de prueba y comparación, no solo como aplicación visual.

---

## 9. Otros archivos útiles

## 9.1 `README.md`

### Qué hace
Resume el proyecto, su ejecución y su alcance general.

## 9.2 `run.bat` y `run.ps1`

### Qué hacen
Facilitan el arranque del sistema desde Windows.

### Por qué son útiles
Permiten ejecutar la aplicación sin necesidad de activar manualmente el entorno.

---

## 10. Resumen conceptual de dependencias internas

Una forma simple de explicarlo es:

1. `main.py` inicia todo.
2. `simulation_engine.py` mantiene el estado real.
3. `services` aplican reglas.
4. `domain` define los objetos del sistema.
5. `ui` muestra todo al usuario.

---

## 11. Qué decir si el jurado pregunta por módulos

Una respuesta clara sería:

“El sistema está organizado de forma modular. La interfaz está separada de la lógica de simulación. Las entidades principales se definen en el dominio, las reglas operativas se agrupan en servicios y el motor de simulación centraliza el comportamiento del sistema. Esto mejora mantenibilidad, claridad y defendibilidad técnica.”
