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
├─ run.bat
├─ run.ps1
└─ README.md
```

---

## Requisitos
- Python 3.11 o superior recomendado
- PySide6
- Windows PowerShell o terminal compatible para los scripts de arranque

---

## Instalación

### Opción 1. Instalación manual
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

### Opción 2. Ejecución rápida recomendada
Sin activar manualmente el entorno:

```powershell
.\run.bat
```

Si deseas forzar reinstalación de dependencias:

```powershell
.\run.bat --reinstall
```

También puedes usar:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1
```

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
- documentación académica y técnica.

No incluye actualmente:

- base de datos;
- exportación de reportes;
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
