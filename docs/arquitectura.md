# Arquitectura

## 1. Introducción arquitectónica
La arquitectura del sistema fue diseñada con un criterio central: **separar la observación, la gestión de operador y la lógica interna de simulación**.

Esta decisión hace que el sistema sea:

- más claro;
- más mantenible;
- más profesional;
- más defendible ante un jurado.

---

## 2. Estructura general

El sistema se apoya en tres grandes componentes:

| Componente | Función |
|---|---|
| Radar Operativo | Visualizar la situación espacial |
| Centro de Control | Gestionar operación, configuración y alertas |
| Motor de simulación compartido | Mantener el estado y ejecutar la lógica |
| Runtime headless | Ejecutar corridas reproducibles sin abrir interfaz |

---

## 3. Ventanas del sistema

### 3.1 Radar Operativo
Es la ventana principal de observación.

Su función es:

- representar el radar 2D;
- mostrar unidades, rutas y trayectorias;
- reflejar el escenario activo;
- permitir seleccionar unidades;
- permitir asignar objetivos mediante clic.

Se diseñó para ocupar la mayor parte del espacio visual y parecerse a una vista operativa real.

### 3.2 Centro de Control
Es la ventana de gestión del operador.

Contiene:

- estado global;
- control de simulación;
- selección de escenarios;
- selección de modo;
- parámetros operativos;
- alertas;
- detalle de unidad seleccionada;
- resumen de enjambres;
- lista de unidades activas;
- gráficos en vivo;
- exportación de informes.

Su función es concentrar la interacción sin saturar el radar.

---

## 4. Comunicación entre ventanas

Las dos ventanas se comunican a través del mismo estado interno. No son dos aplicaciones separadas.

Esto significa que:

- si se selecciona una unidad en el radar, el Centro de Control muestra esa unidad;
- si se cambia un parámetro en el Centro de Control, el radar se actualiza;
- si se genera una alerta, ambas vistas quedan sincronizadas.
- si se crea una unidad desde el Centro de Control, se integra al escenario activo.

La ventaja de esta arquitectura es que evita inconsistencias.

---

## 5. Motor de simulación compartido

### ¿Qué es?
Es el núcleo lógico del sistema.

### ¿Qué hace?
Gestiona:

- las unidades;
- el tiempo de simulación;
- el escenario activo;
- el modo operativo;
- el movimiento;
- la batería;
- las alertas;
- la selección de unidades.
- las métricas de la corrida.

### ¿Por qué es compartido?
Porque garantiza una única fuente de verdad. De esta forma:

- no hay estados duplicados;
- no hay divergencia entre ventanas;
- el sistema conserva coherencia.

---

## 6. Capas lógicas del sistema

| Capa | Función |
|---|---|
| Interfaz | Mostrar información y recibir acciones |
| Servicios | Aplicar reglas de escenarios, modos, enjambres y alertas |
| Dominio | Definir entidades como unidad, alerta y waypoint |
| Simulación | Actualizar posiciones, tiempos y estados |
| Entrada/salida | Guardar configuraciones y exportar informes |
| Runtime | Ejecutar corridas headless |
| Configuración | Contener parámetros globales |

### 6.1 Interfaz
Incluye las ventanas visibles y los paneles. Su tarea es representar, no decidir la lógica profunda.

### 6.2 Servicios
Aquí se agrupan decisiones específicas como:

- aplicación de escenarios;
- asignación de enjambres;
- evaluación de alertas;
- organización de modos operativos.
- retorno a base y recarga;
- acumulación de métricas.

### 6.3 Dominio
Define qué es cada elemento esencial del sistema:

- una unidad;
- una alerta;
- un objetivo.

### 6.4 Simulación
Es donde evoluciona el sistema con el tiempo:

- movimiento;
- trayectoria;
- batería;
- estado;
- alertas dinámicas.

La simulación puede avanzar por temporizador Qt en la interfaz o por pasos lógicos en modo headless. Esto permite reutilizar la lógica sin depender de clics manuales.

### 6.5 Configuración
Agrupa valores comunes como:

- nombres de escenarios;
- tamaños;
- colores;
- límites;
- umbrales.

---

## 7. ¿Por qué dos ventanas?

### Problema anterior
Cuando radar y controles estaban demasiado juntos, la interfaz se saturaba y el radar perdía protagonismo.

### Solución adoptada
Separar la aplicación en:

- una ventana para observar;
- una ventana para controlar.

### Justificación
Esta decisión:

- mejora legibilidad;
- organiza mejor la información;
- facilita la explicación académica;
- hace más profesional la demostración.

---

## 8. Gestión de escenarios

Antes, elegir un escenario aplicaba cambios automáticamente. Eso se corrigió con una configuración previa.

### ¿Por qué?
Porque es más coherente que el operador:

- seleccione escenario;
- revise la configuración;
- confirme la aplicación.

Esto hace que el sistema parezca más controlado y menos automático.

Cuando se agrega una unidad después de aplicar un escenario, el motor vuelve a asignar enjambre y modo para que la nueva unidad reciba ruta y waypoint. Así se evita que quede detenida o fuera de misión.

---

## 9. Gestión de enjambres

El sistema incorpora el concepto de enjambre como grupo operativo simple.

### ¿Por qué?
Porque mejora el nivel conceptual del prototipo. En vez de pensar solo en unidades individuales, ahora se puede explicar la operación en términos de:

- Enjambre 1 patrulla;
- Enjambre 2 reconoce.

### Ventaja académica
Esto aporta claridad, organización y mejor interpretación del escenario mixto.

---

## 10. Métricas, exportación y modo headless

El sistema incorpora un servicio de métricas que registra información de cada corrida.

### Qué registra
- distancia recorrida;
- batería mínima, promedio y final;
- tiempo por estado;
- alertas por tipo;
- alertas por severidad;
- series temporales por unidad.

### Exportación
La exportación genera:

- `timeseries.csv`;
- `summary.json`.

El CSV sirve para análisis detallado por tick. El JSON sirve para resumen y comparación entre corridas.

### Modo headless
El modo headless permite ejecutar la simulación sin ventanas gráficas.

Esto permite:

- repetir pruebas con semilla;
- validar escenarios;
- generar informes automáticamente;
- comparar configuraciones sin intervención manual.

---

## 11. Conclusión arquitectónica

La arquitectura puede resumirse así:

1. dos ventanas complementarias;
2. un motor compartido;
3. servicios especializados;
4. lógica separada de la interfaz;
5. estructura modular y mantenible;
6. exportación de evidencia;
7. ejecución visual y headless.

Esta arquitectura es suficiente para el alcance del proyecto y sólida para una defensa de tesis.
