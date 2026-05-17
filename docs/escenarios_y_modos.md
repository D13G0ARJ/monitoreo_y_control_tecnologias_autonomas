# Escenarios y Modos

## 1. Diferencia entre escenario y modo

Es muy importante no confundir estos dos conceptos.

| Concepto | Significado |
|---|---|
| Escenario | Define el contexto general de la operación |
| Modo | Define el comportamiento dinámico de las unidades |

En otras palabras:

- el escenario responde a **qué situación se está representando**;
- el modo responde a **cómo actúan las unidades dentro de esa situación**.

---

## 2. Escenarios de simulación

## 2.1 Protección de zona estratégica

### ¿Qué representa?
Representa la vigilancia continua de una zona central protegida.

### ¿Cómo se configura?
Normalmente:

- 8 unidades por defecto;
- un solo enjambre;
- todas las unidades en `E1`;
- rol principal: patrullaje defensivo.

### ¿Qué se ve en el radar?
- zona estratégica central;
- unidades alrededor del perímetro;
- rutas perimetrales;
- operación enfocada en cobertura continua.

### ¿Qué significa en contexto militar académico?
Significa supervisión de perímetro y protección de un espacio de interés. No implica agresión, sino vigilancia.

### ¿Qué decir en la defensa?
“Este escenario representa la supervisión perimetral de una zona estratégica. Las unidades se organizan para patrullar alrededor del área central, permitiendo observar estados, rutas y alertas en una operación simulada.”

---

## 2.2 Reconocimiento de área de interés

### ¿Qué representa?
Representa una misión de exploración o supervisión de puntos específicos.

### ¿Cómo se configura?
Normalmente:

- 7 unidades por defecto;
- un solo enjambre;
- todas las unidades en `E1`;
- rol principal: reconocimiento.

### ¿Qué se ve en el radar?
- puntos de observación;
- rutas secuenciales;
- unidades desplazándose entre múltiples puntos.

### ¿Qué significa en contexto militar académico?
Significa una misión de observación del entorno, búsqueda de información espacial o supervisión de sectores.

### ¿Qué decir en la defensa?
“Este escenario se enfoca en reconocimiento. Las unidades siguen rutas secuenciales sobre puntos de observación definidos, lo que permite demostrar control de rutas, monitoreo de variables y alertas durante una misión simulada.”

---

## 2.3 Vigilancia y reconocimiento combinado

### ¿Qué representa?
Representa una operación mixta donde un grupo patrulla y otro grupo reconoce.

### ¿Cómo se configura?
Normalmente:

- 10 unidades por defecto;
- dos enjambres;
- `E1` en patrullaje;
- `E2` en reconocimiento.

### ¿Qué se ve en el radar?
- un grupo orbitando o patrullando;
- otro grupo recorriendo puntos de observación;
- etiquetas que diferencian claramente a E1 y E2.

### ¿Qué significa en contexto militar académico?
Representa coordinación básica de grupos operativos dentro de una misión de vigilancia y reconocimiento.

### ¿Qué decir en la defensa?
“En este escenario el sistema demuestra coordinación operativa básica: un enjambre mantiene patrullaje defensivo del perímetro y otro realiza reconocimiento de puntos de interés.”

---

## 3. Configuración operativa de escenarios

Antes de aplicar un escenario, el sistema abre el diálogo **Configurar escenario**.

Allí el operador define:

- cantidad de unidades;
- número de enjambres;
- distribución;
- usar unidades existentes o reemplazar;
- velocidad máxima;
- altitud objetivo;
- radio de vigilancia;
- separación mínima;
- umbral de batería baja;
- si inicia automáticamente o no.

### ¿Por qué esto es importante?
Porque da control real al operador y hace que el sistema sea más profesional y defendible.

### Configuraciones reutilizables
El sistema permite guardar y cargar configuraciones de escenario en JSON. Estos archivos conservan:

- escenario;
- cantidad de unidades;
- cantidad de enjambres;
- distribución;
- modo;
- velocidad máxima;
- altitud;
- radio de vigilancia;
- separación mínima;
- umbral de batería baja;
- radio protegido;
- puntos de observación;
- opción de inicio automático.

Al cargar una configuración, el sistema aplica estos valores y vuelve a organizar unidades, enjambres y rutas.

### Agregar unidades después de aplicar un escenario
Si el operador usa `Crear unidad` después de cargar o aplicar un escenario, la nueva unidad no queda aislada. El sistema la integra a la misión activa:

- actualiza el número de unidades configuradas;
- reasigna enjambres;
- aplica el modo vigente;
- asigna ruta y waypoint;
- calcula la distancia inicial al objetivo.

Esto permite escalar una demostración sin tener que cerrar ni volver a crear el escenario completo.

---

## 4. Modos operativos

## 4.1 Modo Defensivo

### Propósito
Mantener vigilancia perimetral continua.

### Comportamiento de las unidades
- siguen una ruta circular;
- van pasando de un punto perimetral al siguiente;
- no se quedan en un único destino;
- sostienen patrullaje continuo.

### Comportamiento visual
Se observa movimiento circular o perimetral.

### Diferencia con otros modos
No busca explorar puntos dispersos, sino proteger un perímetro.

### Justificación en la tesis
Representa una misión clara de vigilancia y protección de zona.

---

## 4.2 Modo Reconocimiento

### Propósito
Recorrer secuencialmente puntos de observación.

### Comportamiento de las unidades
- reciben rutas de varios waypoints;
- pasan automáticamente de un punto al siguiente;
- realizan barridos o recorridos de exploración.

### Comportamiento visual
Se ve desplazamiento interno más variable que en el modo defensivo.

### Diferencia con otros modos
Se centra en inspección de sectores, no en cobertura perimetral.

### Justificación en la tesis
Permite mostrar la dimensión de exploración y supervisión de áreas de interés.

---

## 4.3 Modo Mixto

### Propósito
Combinar patrullaje y reconocimiento en la misma simulación.

### Comportamiento de las unidades
- un grupo patrulla;
- otro grupo reconoce;
- la operación queda dividida por roles.

### Comportamiento visual
Se aprecia claramente un grupo alrededor del perímetro y otro grupo en rutas internas.

### Diferencia con otros modos
Integra dos funciones operativas a la vez.

### Justificación en la tesis
Es el modo que mejor demuestra coordinación multiunidad y organización por grupos.
