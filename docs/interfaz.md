# Interfaz

## 1. Introducción
La interfaz fue diseñada para parecer un sistema de monitoreo profesional, pero manteniendo claridad y simplicidad.

Su objetivo es:

- facilitar la interpretación operativa;
- reducir saturación visual;
- mostrar información útil sin confundir al usuario.

---

## 2. Ventana Radar Operativo

### 2.1 Radar
Es el área central donde se representa el entorno de operación.

Representa el espacio simulado en el que se mueven las unidades.

### 2.2 Círculos concéntricos
Sirven como referencia visual de distancia respecto al centro del radar.

Ayudan a interpretar si una unidad está más cerca de la zona central o del límite de vigilancia.

### 2.3 Barrido radar
Es el efecto visual rotatorio que imita el funcionamiento de un radar.

Su función es reforzar la sensación de supervisión continua.

### 2.4 Zona estratégica
Es un área central destacada en el radar.

Representa el espacio que debe protegerse o supervisarse según el escenario.

### 2.5 Puntos de observación
Son puntos visibles que representan zonas de interés para tareas de reconocimiento.

### 2.6 Unidades autónomas
Son los puntos móviles del radar.

Cada una representa una entidad autónoma simulada con estado, batería, velocidad y misión.

### 2.7 Etiquetas de unidades
Las etiquetas `U01`, `U02`, `U03` identifican cada unidad de forma única.

### 2.8 Etiquetas de rol
Las etiquetas operativas muestran identidad, enjambre y función:

- `U01 [E1-P]`
- `U03 [E2-R]`
- `U04 [E1-T]`
- `U05 [E2-M]`

| Símbolo | Significado |
|---|---|
| E1 | Enjambre 1 |
| E2 | Enjambre 2 |
| P | Patrullaje |
| R | Reconocimiento |
| T | Tarea temporal |
| M | Control manual |

### 2.9 Trayectorias
Muestran el camino reciente que ya recorrió una unidad.

### 2.10 Rutas
Muestran el tramo activo o próximo de movimiento.

No muestran la ruta completa si eso genera saturación visual.

### 2.11 Waypoints
Son los puntos objetivo a los que una unidad debe dirigirse.

### 2.12 Colores
Los colores ayudan a identificar roles y estados:

| Color | Interpretación |
|---|---|
| Verde / cian | Patrullaje o condición normal |
| Azul / amarillo | Reconocimiento o ruta activa |
| Amarillo / naranja | Advertencia |
| Rojo | Crítico o sin batería |
| Gris | Detenido o fuera de operación |

### 2.13 Leyenda
Resume el significado básico de colores y tipos de rol.

### 2.14 HUD
Es un resumen visual dentro del radar que muestra:

- escenario activo;
- modo activo;
- unidades activas;
- alertas activas.

Su finalidad es dar contexto inmediato sin obligar al usuario a mirar la otra ventana.

---

## 3. Ventana Centro de Control

El Centro de Control está organizado en pestañas para evitar saturación.

---

## 4. Pestaña Estado

### ¿Qué muestra?
Muestra la condición general del sistema.

Incluye:

- escenario activo;
- modo activo;
- unidades activas;
- unidades configuradas;
- enjambres activos;
- alertas activas;
- estado de la simulación;
- tiempo;
- parámetros principales;
- unidad seleccionada;
- resumen de enjambres.

### ¿Cómo se interpreta?
Es la vista ejecutiva de la operación. Permite saber rápidamente qué está pasando.

### Unidad seleccionada
Muestra:

- ID;
- enjambre;
- rol de enjambre;
- rol actual;
- tarea;
- posición;
- velocidad;
- altitud;
- distancia al objetivo;
- batería;
- alertas activas;
- estado.

Si no hay selección, aparece el mensaje: **“Seleccione una unidad en el radar”**.

### Enjambres
Cada enjambre muestra:

- cantidad de unidades;
- rol;
- estado general.

---

## 5. Pestaña Control

### Selector de escenario
Permite elegir el escenario general.

Cuando se usa, el sistema abre una ventana de configuración antes de aplicar cambios.

### Selector de modo
Permite cambiar el comportamiento operativo de las unidades existentes.

### Asignación manual
Permite elegir entre:

- tarea temporal;
- control manual.

### Botones

| Botón | Función |
|---|---|
| Crear unidad | Añade una nueva unidad |
| Asignar objetivo | Prepara la asignación de un objetivo en el radar |
| Iniciar | Activa la simulación |
| Pausar | Detiene temporalmente la simulación |
| Reiniciar | Restablece la simulación del escenario actual |

---

## 6. Pestaña Parámetros

| Parámetro | Qué controla | Por qué es importante |
|---|---|---|
| Velocidad máxima | Límite global de desplazamiento | Evita movimientos irreales |
| Altitud | Altitud simulada de referencia | Añade variable operacional |
| Separación mínima | Distancia segura entre unidades | Permite alertas de proximidad |
| Radio de vigilancia | Tamaño del área de operación | Define límites de zona |
| Batería baja | Umbral de advertencia | Permite monitoreo preventivo |
| Unidades activas | Cantidad de unidades | Ajusta la escala del escenario |
| Sonido de alertas | Activa o desactiva aviso sonoro | Mejora percepción de incidencias |

---

## 7. Pestaña Alertas

Muestra el historial reciente de alertas.

Cada alerta contiene:

- severidad;
- timestamp;
- unidad;
- enjambre si aplica;
- descripción.

### Severidad
| Prefijo | Significado |
|---|---|
| INFO | Información |
| WARN | Advertencia |
| CRIT | Crítica |

### Sonido
Si está activado:

- las advertencias generan aviso simple;
- las alertas críticas generan un aviso más notorio.

### Lógica de generación
Las alertas se generan por:

- batería baja;
- batería crítica;
- sin batería;
- fuera de zona;
- proximidad entre unidades;
- objetivo alcanzado.

---

## 8. Interpretación global de la interfaz

La lectura correcta del sistema es:

1. el radar muestra la situación espacial;
2. el Centro de Control muestra el estado lógico y operativo;
3. el operador combina ambas vistas para supervisar y actuar.

Esto hace que la interfaz sea clara, profesional y defendible.
