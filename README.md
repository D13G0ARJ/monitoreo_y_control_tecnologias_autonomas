# Sistema de Monitoreo y Control de Tecnologías Autónomas

## Descripción
Este repositorio contiene el desarrollo de un sistema de escritorio orientado al **monitoreo y control de tecnologías autónomas en un entorno simulado**, mediante una **interfaz gráfica tipo radar**.

El proyecto fue concebido como una propuesta académica para la tesis:

**“Diseño de un sistema de monitoreo y control de tecnologías autónomas mediante una interfaz gráfica tipo radar en un entorno simulado para aplicaciones en el área de defensa y vigilancia militar en la UNEFA”**

Su propósito es demostrar, en un entorno local y controlado, cómo pueden integrarse:

- monitoreo visual de múltiples unidades;
- control básico de movimiento;
- escenarios operativos simulados;
- organización por enjambres;
- alertas y estados operativos;
- una interfaz especializada tipo radar.

---

## Enfoque del proyecto
El sistema está orientado a:

- vigilancia;
- patrullaje;
- supervisión de zonas estratégicas;
- reconocimiento de áreas de interés;
- coordinación operativa simulada.

No está orientado a:

- hardware real;
- drones reales;
- GPS real;
- mapas reales;
- armamento;
- ataques reales;
- daño o letalidad;
- inteligencia artificial avanzada;
- base de datos en la versión actual.

---

## Capacidades principales

### Visualización y monitoreo
- Radar 2D con círculos concéntricos y barrido visual.
- Zona estratégica y puntos de observación.
- Unidades autónomas con etiquetas operativas.
- Rutas activas y trayectorias históricas.
- HUD con escenario, modo, unidades activas y alertas.

### Control operativo
- Configuración previa de escenarios.
- Modos operativos: `Defensivo`, `Reconocimiento` y `Mixto`.
- Asignación de objetivos manuales.
- Tareas temporales sin perder la misión original.
- Control manual de unidades individuales.

### Organización por grupos
- Gestión simple de enjambres operativos.
- Escenario combinado con división entre patrullaje y reconocimiento.
- Visualización de etiquetas como `U01 [E1-P]` y `U04 [E2-R]`.

### Supervisión de estado
- Estado global del sistema.
- Estado detallado de unidad seleccionada.
- Batería, velocidad, posición, distancia al objetivo y rol.
- Alertas con severidad `INFO`, `WARN` y `CRIT`.
- Sonido opcional de alertas.
- Retorno automático a base por batería baja y recarga simulada.
- Exportación de informes en CSV/JSON.
- Ejecución headless determinista para pruebas de regresión.

---

## Arquitectura general
El sistema está organizado con una arquitectura modular y un **motor de simulación compartido**.

### Componentes principales
- **Radar Operativo**: ventana principal de observación.
- **Centro de Control**: ventana secundaria de gestión.
- **Motor de simulación**: núcleo lógico que mantiene el estado del sistema.

### Organización del código
```text
tesis/
├─ main.py
├─ app/
│  ├─ config/
│  ├─ domain/
│  ├─ services/
│  ├─ simulation/
│  └─ ui/
├─ docs/
├─ requirements.txt
└─ README.md
```

---

## Requisitos
- Python 3.12 recomendado
- uv (manejo de entornos y dependencias)
- PySide6
- Terminal Bash o PowerShell

---

## Instalación
Consulta la guía de setup para los pasos detallados en Linux y Windows:

- [Setup de desarrollo](docs/setup-dev.md)

---

## Comandos principales
```bash
./setup.sh
./run.sh
./test.sh
uv run python main.py
uv run python main.py --headless --scenario "Protección de zona estratégica" --duration 30 --seed 1 --out run_output
uv run --group dev ruff check app tests
```

El modo `--headless` ejecuta la simulación sin abrir ventanas Qt y escribe `timeseries.csv` y `summary.json` en la carpeta indicada por `--out`.

---

## Flujo básico de uso
1. Abrir la aplicación.
2. Seleccionar un escenario desde el Centro de Control.
3. Configurar cantidad de unidades, enjambres y parámetros principales.
4. Aplicar el escenario.
5. Iniciar la simulación.
6. Seleccionar una unidad en el radar.
7. Asignar una tarea temporal o control manual si es necesario.
8. Supervisar alertas, batería y estado operativo.
9. Pausar o reiniciar según la demostración requerida.

Para una guía práctica paso a paso, consulta el manual de usuario en la documentación.

---

## Documentación
El repositorio incluye documentación académica y operativa en la carpeta [`docs/`](docs/).

### Índice principal
- [Índice de documentación](docs/indice_documentacion.md)

### Documentos disponibles
- [Sistema general](docs/sistema_general.md)
- [Arquitectura](docs/arquitectura.md)
- [Interfaz](docs/interfaz.md)
- [Escenarios y modos](docs/escenarios_y_modos.md)
- [Control y lógica](docs/control_y_logica.md)
- [Manual de usuario](docs/manual_usuario.md)
- [Descripción de módulos](docs/descripcion_modulos.md)
- [Defensa](docs/defensa.md)
- [Setup de desarrollo](docs/setup-dev.md)

### Uso recomendado de la documentación
- Si deseas entender el sistema desde cero: comienza por `sistema_general.md`.
- Si deseas aprender a usarlo: revisa `manual_usuario.md`.
- Si deseas prepararte para la defensa: revisa `defensa.md`.
- Si deseas explicar el desarrollo interno: revisa `descripcion_modulos.md`.

---

## Alcance actual
La versión actual del sistema incluye:

- simulación local;
- interfaz tipo radar;
- control básico;
- escenarios operativos;
- enjambres simples;
- alertas;
- batería y estados operativos;
- retorno a base y recarga simulada;
- métricas e informes exportables;
- modo headless para corridas reproducibles;
- documentación académica y técnica.

No incluye actualmente:

- base de datos;
- mapas reales;
- hardware real;
- comunicación real entre unidades;
- PID;
- simulación 3D;
- inteligencia artificial avanzada.

---

## Valor académico
Este proyecto busca demostrar que es posible construir una plataforma académica de monitoreo y control de tecnologías autónomas en entorno simulado, con una interfaz clara, lógica operativa defendible y organización modular suficiente para ser estudiada, explicada y ampliada.

---

## Autoría y contexto
Desarrollado como proyecto académico de tesis en el contexto de la UNEFA, con enfoque en simulación aplicada al área de defensa y vigilancia militar desde una perspectiva segura, no letal y orientada a supervisión y reconocimiento.
