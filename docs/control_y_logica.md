# Control y Lógica

## 1. Control de unidades

### 1.1 ¿Qué es una unidad autónoma?
Es una entidad simulada con:

- posición;
- velocidad;
- altitud;
- batería;
- estado;
- rol;
- tarea actual;
- posible pertenencia a un enjambre.

### 1.2 ¿Qué es un waypoint?
Es un punto objetivo al que una unidad debe dirigirse.

### 1.3 ¿Qué es una ruta?
Es una secuencia de waypoints.

### 1.4 ¿Qué es una trayectoria?
Es el rastro del movimiento que la unidad ya realizó.

La diferencia clave es:

- la ruta indica el plan;
- la trayectoria indica el recorrido ya ejecutado.

---

## 2. ¿Cómo se mueve una unidad?

El movimiento sigue una lógica simple:

1. la unidad conoce su posición actual;
2. el sistema conoce su objetivo;
3. calcula hacia dónde debe avanzar;
4. actualiza la posición en pequeños pasos;
5. repite este proceso hasta llegar al objetivo.

---

## 3. ¿Qué es control proporcional?

Es una estrategia simple en la que la respuesta del sistema depende de qué tan lejos está la unidad de su objetivo.

### Explicación sencilla
- si la unidad está lejos, avanza con mayor decisión;
- si está cerca, el sistema suaviza el movimiento.

### ¿Por qué se eligió?
Porque es:

- más fácil de explicar;
- suficiente para el alcance del prototipo;
- adecuado para demostrar control básico de navegación.

---

## 4. ¿Cómo sabe la unidad que llegó?

El sistema usa una tolerancia. Si la unidad está suficientemente cerca del waypoint:

- se considera que llegó;
- puede detenerse;
- o puede pasar al siguiente punto si forma parte de una ruta.

---

## 5. Tipos de control

## 5.1 Control automático

### ¿Qué es?
Es el comportamiento que proviene del escenario o del modo operativo.

### ¿Cómo funciona?
El sistema asigna rutas de patrullaje o reconocimiento según el rol de la unidad o del enjambre.

### ¿Cuándo se usa?
Cuando se desea que las unidades sigan una misión estructurada sin intervención individual directa.

## 5.2 Tarea temporal

### ¿Qué es?
Es una intervención puntual del operador sobre una unidad.

### ¿Cómo funciona?
La unidad recibe un objetivo manual temporal pero conserva la referencia de su misión original.

Cuando termina la tarea:

- vuelve a la misión previa.

### ¿Por qué existe?
Permite intervenir sin romper el escenario general.

## 5.3 Control manual

### ¿Qué es?
Es una intervención directa del operador donde la unidad deja su conducta automática.

### ¿Cómo funciona?
Recibe un objetivo manual y queda bajo control específico del operador.

### ¿Por qué existe?
Porque muestra un nivel más alto de control individual.

---

## 6. Enjambres operativos

### ¿Qué es un enjambre?
Es un grupo operativo de unidades.

No implica inteligencia artificial avanzada; es una estructura organizativa simple.

### ¿Por qué se usa?
Porque permite pasar de una lógica de unidades aisladas a una lógica de grupos coordinados.

### ¿Cómo se asignan?
Según el escenario:

- escenario defensivo: todas en `E1` patrullaje;
- escenario de reconocimiento: todas en `E1` reconocimiento;
- escenario combinado: `E1` patrullaje y `E2` reconocimiento.

### ¿Cómo se visualizan?
Con etiquetas como:

- `E1-P`
- `E2-R`

### ¿Cómo funcionan en el escenario mixto?
Un grupo patrulla mientras el otro reconoce. Esto se ve tanto en el radar como en el Centro de Control.

---

## 7. Sistema de batería

## 7.1 Batería normal
La unidad opera normalmente.

## 7.2 Batería baja
Se activa por debajo del umbral configurable.

### Qué ocurre
- se genera advertencia;
- la unidad sigue operando;
- queda visualmente marcada.

## 7.3 Batería crítica
Se activa en un nivel muy bajo.

### Qué ocurre
- se genera alerta crítica;
- la velocidad se reduce automáticamente;
- la capacidad operativa se degrada.

## 7.4 Sin batería
Se activa cuando la batería llega a cero.

### Qué ocurre
- la unidad se detiene por completo;
- no sigue waypoints;
- no patrulla;
- no reconoce;
- queda visible como fuera de operación.

### ¿Por qué es importante?
Porque le da coherencia realista al sistema.

---

## 8. Sistema de alertas

### ¿Cómo se generan?
Cuando el motor detecta condiciones relevantes durante la simulación.

### Tipos principales
- objetivo alcanzado;
- batería baja;
- batería crítica;
- sin batería;
- fuera de zona;
- proximidad entre unidades.

### Severidad
| Nivel | Significado |
|---|---|
| INFO | Información |
| WARN | Advertencia |
| CRIT | Condición crítica |

### Relación con enjambres
Cuando es posible, la alerta muestra también el enjambre de la unidad afectada.

### Lógica de no repetición
El sistema evita repetir infinitamente la misma alerta para no saturar al operador.

---

## 9. Variables del sistema

## 9.1 Variables visibles

| Variable | Explicación |
|---|---|
| ID | Identificador único de la unidad |
| Posición | Ubicación actual en el radar |
| Velocidad | Rapidez de desplazamiento |
| Altitud | Altitud simulada |
| Estado | Condición actual de la unidad |
| Batería | Nivel de energía |
| Distancia | Distancia al objetivo |
| Rol | Función operativa actual |
| Tarea | Tipo de control aplicado |

## 9.2 Variables internas

| Variable | Explicación |
|---|---|
| Waypoint | Objetivo actual |
| Ruta | Secuencia de puntos por recorrer |
| Trayectoria | Historial de movimiento |
| Radio de vigilancia | Límite del entorno |
| Separación mínima | Distancia de seguridad |
| Enjambre | Grupo operativo |
| Rol de enjambre | Función grupal |
| Tiempo de simulación | Tiempo interno del sistema |

---

## 10. Justificación técnica

### ¿Por qué simulación?
Porque reduce costo, riesgo y dependencia de infraestructura real.

### ¿Por qué interfaz tipo radar?
Porque permite una lectura espacial clara y coherente con vigilancia y supervisión.

### ¿Por qué control proporcional simple?
Porque es suficiente, claro y defendible para el alcance del proyecto.

### ¿Por qué arquitectura modular?
Porque separa la lógica de la interfaz y facilita mantenimiento.

### ¿Por qué enjambres operativos?
Porque mejoran la organización conceptual de la simulación y la claridad del escenario mixto.
