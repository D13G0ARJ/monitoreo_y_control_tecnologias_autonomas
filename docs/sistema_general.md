# Sistema General

## Propósito de esta documentación
Este documento explica la visión general del sistema desarrollado para la tesis:

**“Diseño de un sistema de monitoreo y control de tecnologías autónomas mediante una interfaz gráfica tipo radar en un entorno simulado para aplicaciones en el área de defensa y vigilancia militar en la UNEFA”**

Su propósito es servir como base de estudio, defensa académica y apoyo para la redacción formal del trabajo de grado.

---

## 1. Descripción general del sistema

### 1.1 ¿Qué es el sistema?
Es una plataforma informática de simulación, monitoreo y control que representa múltiples tecnologías autónomas dentro de una interfaz gráfica tipo radar.

En términos prácticos, es un simulador donde el operador puede:

- observar unidades móviles en un radar;
- organizarlas por escenarios;
- supervisar su estado;
- intervenir sobre ellas;
- recibir alertas;
- revisar métricas;
- exportar informes;
- analizar comportamientos de patrullaje y reconocimiento.

### 1.2 ¿Para qué sirve?
Sirve para demostrar de manera académica cómo puede construirse un sistema capaz de integrar:

- visualización espacial;
- monitoreo de variables operativas;
- control básico del movimiento;
- organización por grupos operativos;
- manejo de alertas;
- retorno automático a base y recarga;
- métricas exportables;
- ejecución headless reproducible;
- simulación de escenarios de vigilancia y defensa.

### 1.3 ¿Qué problema resuelve?
Resuelve un problema de representación y coordinación. En vez de trabajar con ideas abstractas sobre tecnologías autónomas, el sistema permite verlas operando dentro de un entorno simulado, con reglas claras y una interfaz especializada.

Eso permite:

- convertir conceptos teóricos en una demostración funcional;
- observar varias unidades al mismo tiempo;
- coordinar grupos de unidades;
- justificar decisiones operativas y de diseño ante un jurado.

### 1.4 ¿En qué contexto se aplica?
Se aplica en un contexto académico de:

- vigilancia;
- patrullaje;
- supervisión de zonas estratégicas;
- reconocimiento de áreas de interés;
- coordinación de tecnologías autónomas simuladas.

### 1.5 ¿Qué NO hace el sistema?
El sistema tiene límites claros:

- no controla hardware real;
- no usa drones reales;
- no se conecta con equipos militares reales;
- no representa ataques reales;
- no representa daño, destrucción ni letalidad;
- no usa GPS real;
- no usa mapas reales;
- no implementa armamento;
- no incorpora inteligencia artificial avanzada;
- no utiliza base de datos en la versión actual.

### 1.6 ¿Cómo se relaciona con el título de la tesis?
La relación con el título es directa:

- **sistema de monitoreo y control**: supervisa estados y permite intervención del operador;
- **tecnologías autónomas**: las unidades simuladas representan entidades autónomas;
- **interfaz tipo radar**: el radar es la visualización principal;
- **entorno simulado**: no hay conexión física con plataformas reales;
- **defensa y vigilancia militar**: los escenarios fueron diseñados para patrullaje, vigilancia y reconocimiento en un contexto académico seguro.

---

## 2. Enfoque conceptual

### 2.1 Monitoreo
Monitorear significa observar de forma continua el estado del sistema y de sus unidades:

- posición;
- velocidad;
- batería;
- estado;
- tarea actual;
- distancia al objetivo;
- alertas.
- métricas de la corrida.

### 2.2 Control
Controlar significa influir sobre el comportamiento de las unidades. En este sistema, el control se expresa en:

- asignación de objetivos;
- cambio de modos operativos;
- organización por escenarios;
- tareas temporales;
- control manual de una unidad.

### 2.3 Simulación
La simulación permite demostrar el sistema sin recurrir a plataformas reales. Eso reduce:

- costo;
- riesgo;
- dependencia de infraestructura;
- complejidad técnica innecesaria.

---

## 3. Flujo completo de uso del sistema

### Paso 1. Abrir el sistema
Al iniciar la aplicación se abren dos ventanas:

- **Radar Operativo**
- **Centro de Control**

Internamente, ambas dependen del mismo motor de simulación.

### Paso 2. Seleccionar escenario
El operador elige un escenario desde el Centro de Control.

Internamente, el sistema no lo aplica inmediatamente; primero solicita confirmación y configuración.

### Paso 3. Configurar escenario
Aparece el diálogo **Configurar escenario**, donde se define:

- cantidad de unidades;
- número de enjambres;
- distribución;
- uso de unidades existentes o reemplazo;
- velocidad máxima;
- altitud objetivo;
- radio de vigilancia;
- separación mínima;
- umbral de batería baja;
- inicio automático.

### Paso 4. Aplicar escenario
Cuando el operador confirma:

- el sistema ajusta los parámetros globales;
- crea o reutiliza unidades;
- organiza los enjambres;
- aplica el modo correspondiente;
- calcula los waypoints y distancias iniciales al objetivo;
- actualiza el radar y el Centro de Control.

Si el operador cancela, no cambia nada.

### Paso 5. Visualizar el radar
El Radar Operativo muestra:

- unidades;
- rutas;
- zona estratégica;
- puntos de observación;
- escenario activo;
- modo activo;
- resumen de alertas.

### Paso 6. Seleccionar unidad
Al hacer clic sobre una unidad en el radar o en la lista de unidades activas:

- la unidad queda seleccionada;
- el Centro de Control muestra su detalle.

### Paso 7. Asignar objetivo
El operador puede asignar:

- una **tarea temporal**;
- un **control manual**.

Internamente, el sistema crea un waypoint y actualiza la misión de la unidad.

### Paso 8. Cambiar modo
El modo operativo puede cambiarse sin crear nuevas unidades.

Si no existen unidades activas, el sistema informa que primero debe crearse o cargarse un escenario.

Si se crea una unidad nueva después de aplicar un escenario, el sistema la integra automáticamente al escenario activo. La unidad recibe enjambre, rol, ruta, waypoint y distancia inicial al objetivo.

### Paso 9. Generar alertas
Durante la simulación se generan alertas por eventos como:

- batería baja;
- batería crítica;
- sin batería;
- fuera de zona;
- proximidad entre unidades;
- objetivo alcanzado.
- retorno a base iniciado;
- recarga completada.

### Paso 10. Pausar o reiniciar
El operador puede:

- pausar la simulación;
- reiniciarla.

Al reiniciar, el sistema conserva la estructura general del escenario actual y restablece la misión operativa.

### Paso 11. Exportar y analizar
El operador puede exportar la corrida en CSV y JSON.

El sistema registra:

- posición por tick;
- estado;
- batería;
- velocidad;
- rol y tarea;
- objetivo activo;
- distancia al objetivo;
- alertas activas;
- resumen de distancias, batería y tiempos por estado.

---

## 4. Valor académico del sistema

### 4.1 ¿Por qué es defendible?
Porque integra de manera coherente:

- una arquitectura modular;
- una interfaz tipo radar;
- control básico;
- monitoreo de variables;
- gestión de grupos operativos;
- alertas;
- informes exportables;
- corridas reproducibles;
- simulación de escenarios.

### 4.2 ¿Qué aporta?
Aporta una propuesta funcional para demostrar cómo podría organizarse un sistema de supervisión y control de tecnologías autónomas en contexto académico, sin necesidad de infraestructura real.

### 4.3 ¿Qué se debe resaltar en la defensa?
Se debe resaltar que:

- es un sistema académico y simulado;
- no busca reproducir combate real;
- demuestra coordinación, vigilancia y control;
- integra visualización, lógica operativa y supervisión.

---

## Relación con el resto de la documentación

- [Arquitectura](arquitectura.md)
- [Interfaz](interfaz.md)
- [Escenarios y modos](escenarios_y_modos.md)
- [Control y lógica](control_y_logica.md)
- [Defensa](defensa.md)
