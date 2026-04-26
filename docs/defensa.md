# Defensa

## 1. Guion sugerido de 5 a 7 minutos

### 1.1 Apertura
“Buenas tardes. El sistema desarrollado corresponde a una propuesta académica de monitoreo y control de tecnologías autónomas en un entorno simulado, mediante una interfaz gráfica tipo radar, orientada a aplicaciones de vigilancia y defensa en la UNEFA.”

### 1.2 Explicar la estructura general
“El sistema está dividido en dos ventanas: Radar Operativo, que muestra la situación espacial, y Centro de Control, que concentra configuración, supervisión y alertas. Ambas dependen del mismo motor de simulación compartido.”

### 1.3 Mostrar selección de escenario
1. abrir la pestaña Control;
2. seleccionar un escenario;
3. mostrar el diálogo de configuración.

Explicación sugerida:

“Una mejora importante es que el escenario no se aplica automáticamente. El operador primero valida la configuración: unidades, enjambres y parámetros principales.”

### 1.4 Aplicar escenario combinado
Aplicar el escenario **Vigilancia y reconocimiento combinado**.

Explicación sugerida:

“En este escenario, un grupo patrulla el perímetro y otro grupo realiza reconocimiento de puntos de interés. Esto muestra una organización operativa básica por enjambres.”

### 1.5 Explicar el radar
Mostrar:

- zona estratégica;
- unidades;
- etiquetas;
- rutas;
- HUD.

Explicación sugerida:

“Cada unidad aparece con una etiqueta como U01 [E1-P], que indica unidad, enjambre y rol. El radar muestra de forma clara la distribución espacial y el estado general de la operación.”

### 1.6 Explicar los enjambres
Mostrar el resumen de enjambres en el Centro de Control.

Explicación sugerida:

“Dentro del sistema, un enjambre es un grupo operativo lógico. No se trata de inteligencia artificial avanzada, sino de una forma de organizar las unidades por misión.”

### 1.7 Explicar control de unidad
Seleccionar una unidad y asignar una tarea temporal o control manual.

Explicación sugerida:

“Además del control automático por escenario, el operador puede intervenir sobre una unidad específica mediante una tarea temporal o control manual.”

### 1.8 Explicar batería y alertas
Explicación sugerida:

“El sistema supervisa batería, estado y distancia al objetivo. Cuando ocurre un evento relevante, genera alertas con severidad y, si está activado, con señal sonora.”

### 1.9 Cierre
“En síntesis, el sistema demuestra una propuesta académica funcional de monitoreo y control mediante radar, con escenarios simulados, organización por enjambres, control básico y alertas, sin necesidad de hardware real.”

---

## 2. Preguntas del jurado y respuestas sugeridas

### ¿Por qué no usa drones reales?
Porque el objetivo de la tesis es diseñar y validar una solución de software en un entorno simulado, sin asumir el costo y riesgo de operar hardware real.

### ¿Dónde está el control dentro del sistema?
Está en la capacidad de asignar objetivos, cambiar modos, organizar escenarios, intervenir sobre unidades y modificar parámetros operativos.

### ¿Qué controla exactamente el sistema?
Controla variables y comportamientos simulados: movimiento, rutas, velocidad limitada, tareas temporales, control manual y respuesta a condiciones operativas.

### ¿Qué significa monitoreo en este proyecto?
Significa observar continuamente el estado del sistema y de sus unidades.

### ¿Qué significa control en este proyecto?
Significa influir sobre la conducta de las unidades para que cumplan una misión o tarea definida.

### ¿Cómo se aplica al área militar?
Se aplica como propuesta académica para vigilancia, supervisión de zonas estratégicas y reconocimiento en un entorno simulado.

### ¿Cuáles son las limitaciones?
- no hay hardware real;
- no hay mapas reales;
- no hay GPS real;
- no hay IA avanzada;
- no hay base de datos;
- no hay simulación 3D.

### ¿Qué mejoras futuras podrían hacerse?
- persistencia de sesiones;
- exportación de reportes;
- editor de rutas;
- integración con mapas;
- métricas históricas;
- coordinación más avanzada entre grupos.

---

## 3. Glosario

| Término | Definición simple |
|---|---|
| Radar | Interfaz visual que muestra espacialmente unidades y eventos |
| Unidad autónoma | Entidad simulada que se mueve y cumple tareas |
| Enjambre | Grupo operativo de unidades |
| Waypoint | Punto objetivo al que se dirige una unidad |
| Monitoreo | Observación continua del estado del sistema |
| Control | Influencia sobre el comportamiento de las unidades |
| Simulación | Representación virtual de una operación |
| Alerta | Evento que señala una condición importante |
| Patrullaje | Recorrido continuo alrededor de una zona |
| Reconocimiento | Recorrido orientado a observar puntos de interés |
| Escenario | Contexto general de operación |
| Modo operativo | Forma de comportamiento de las unidades |

---

## 4. Recomendación para presentar

Durante la defensa conviene seguir este orden:

1. explicar el problema y el objetivo;
2. mostrar el Radar Operativo;
3. mostrar el Centro de Control;
4. aplicar un escenario;
5. explicar enjambres;
6. mostrar control sobre una unidad;
7. explicar alertas y batería;
8. cerrar con valor académico y mejoras futuras.
