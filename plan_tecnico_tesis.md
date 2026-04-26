# Plan técnico del sistema de monitoreo y control en entorno simulado

## Título de la tesis
**Diseño de un sistema de monitoreo y control de tecnologías autónomas mediante una interfaz gráfica tipo radar en un entorno simulado para aplicaciones en el área de defensa y vigilancia militar en la UNEFA**

## 1. Resumen del sistema a desarrollar
Se propone el desarrollo de un **simulador de monitoreo y control de tecnologías autónomas** con **interfaz gráfica tipo radar**, orientado a la supervisión, vigilancia, patrullaje y reconocimiento en un **entorno 2D simulado**. El sistema representará múltiples unidades autónomas como puntos móviles dentro de una zona estratégica, mostrando su estado operativo, trayectoria, variables básicas y alertas relevantes.

El enfoque es **académico, visual, modular y seguro**: no se conecta a hardware real, no controla equipos militares reales y no modela daño ni armamento. Su propósito es demostrar cómo una arquitectura de software puede integrar **simulación, monitoreo, control básico e interfaz gráfica especializada** para aplicaciones de defensa y vigilancia en contexto universitario.

## 2. Objetivo funcional del software
Diseñar e implementar una aplicación de escritorio que permita:

- Visualizar múltiples unidades autónomas en una interfaz tipo radar.
- Simular movimiento y patrullaje en un plano 2D.
- Monitorear variables operativas básicas por unidad.
- Aplicar control simple sobre navegación y separación.
- Gestionar alertas ante eventos relevantes.
- Evaluar distintos modos operativos simulados en una zona estratégica.

## 3. Alcance del sistema
El prototipo cubrirá:

- Simulación local de múltiples unidades.
- Interfaz de monitoreo tipo centro de control.
- Gestión manual de objetivos y waypoints.
- Modo defensivo, reconocimiento y mixto.
- Alertas básicas y trazado histórico.
- Panel de control y panel de estado.

No requiere:

- Redes distribuidas.
- Sensores reales.
- Telemetría externa.
- Integración con hardware o sistemas militares reales.

## 4. Lo que NO hará el sistema
- No controlará drones, robots o vehículos reales.
- No incluirá armamento, daño, destrucción ni letalidad.
- No ejecutará navegación GPS real ni mapas geográficos reales.
- No usará visión artificial compleja ni IA avanzada como requisito base.
- No implementará control avanzado industrial si no aporta defendibilidad académica.
- No será un sistema táctico real; será un **entorno simulado de supervisión**.

## 5. Tecnología recomendada y justificación

### 5.1 Recomendación principal
| Componente | Tecnología | Justificación |
|---|---|---|
| Lenguaje | Python | Curva de aprendizaje adecuada, rápida implementación y buena defensa académica. |
| GUI | PySide6 | Moderna, robusta, LGPL, adecuada para escritorio y con buen soporte gráfico. |
| Radar 2D | QGraphicsView/QGraphicsScene | Muy conveniente para escenas 2D, capas, trayectorias, zonas y selección de objetos. |
| Temporización | QTimer | Permite ciclo de simulación estable sin complejidad innecesaria. |
| Gráficas auxiliares | PyQtGraph opcional | Útil si luego se agregan series temporales o paneles estadísticos. |
| Persistencia | JSON o SQLite opcional | JSON para configuración simple; SQLite si luego se guardan eventos o sesiones. |

### 5.2 Decisión recomendada
La mejor combinación para esta tesis es **Python + PySide6 + QGraphicsView**.

PyQtGraph es excelente para gráficos numéricos, pero para una interfaz tipo radar con objetos, trayectorias, zonas y selección visual, **QGraphicsView ofrece mayor control visual y arquitectónico**.

### 5.3 Alternativa considerada
Si se quisiera un enfoque más visual o multiplataforma avanzado, podría evaluarse **Qt/QML**, pero para una tesis realizable por estudiantes, **PySide6 con widgets tradicionales es más defendible y manejable**.

## 6. Arquitectura general del sistema
Se recomienda una arquitectura modular por capas:

| Capa | Responsabilidad |
|---|---|
| Presentación | Ventanas, radar, paneles, tablas, formularios y alertas visuales. |
| Aplicación | Coordinación de casos de uso: crear unidad, asignar objetivo, iniciar simulación, cambiar modo. |
| Dominio | Reglas de simulación, control, estados, alertas, movimiento y restricciones. |
| Infraestructura | Configuración, persistencia opcional, exportación, logging y utilidades. |

### 6.1 Patrón recomendado
**MVC/MVP híbrido con separación clara entre GUI y lógica de simulación**.

La interfaz no debe calcular física ni control; solo debe mostrar datos y enviar acciones del usuario.

## 7. Módulos principales
1. Módulo de interfaz principal.
2. Módulo de visualización radar.
3. Módulo de simulación.
4. Módulo de control de unidades.
5. Módulo de gestión de alertas.
6. Módulo de modos operativos.
7. Módulo de datos/configuración.
8. Módulo de registro y reportes opcionales.

## 8. Descripción detallada de cada módulo

### 8.1 Interfaz principal
Contiene la ventana principal, menús, barra de estado, panel lateral y controles globales. Centraliza la interacción del operador con el sistema.

### 8.2 Visualización radar
Renderiza:

- Fondo oscuro.
- Círculos concéntricos o cuadrícula.
- Zona estratégica.
- Unidades autónomas.
- Etiquetas ID.
- Trayectorias históricas.
- Waypoints y objetivos.
- Barrido radar opcional.

### 8.3 Simulación
Administra:

- Tiempo de actualización.
- Posiciones y desplazamientos.
- Estado global de la simulación.
- Reinicio, pausa y avance.
- Generación de eventos simulados.

### 8.4 Control de unidades
Aplica lógica básica de guiado:

- Cálculo de error posición-objetivo.
- Ajuste proporcional de velocidad.
- Límite de velocidad.
- Corrección por separación mínima.
- Corrección por salida de zona.

### 8.5 Gestión de alertas
Detecta y clasifica:

- Batería baja.
- Fuera de zona.
- Proximidad entre unidades.
- Pérdida simulada de señal.
- Objetivo alcanzado.
- Anomalía de movimiento.

### 8.6 Modos operativos
Define reglas por escenario:

- Patrullaje perimetral.
- Reconocimiento hacia punto estratégico.
- Modo mixto con roles distintos por unidad.

### 8.7 Datos/configuración
Gestiona:

- Parámetros globales.
- Cantidad inicial de unidades.
- Velocidad máxima.
- Radio de vigilancia.
- Umbrales de alerta.
- Colores, estilos y preferencias.

### 8.8 Registro/reportes opcionales
Permite guardar:

- Eventos de alerta.
- Trayectorias resumidas.
- Estados por unidad.
- Capturas o exportes académicos.

## 9. Modelo de datos inicial
| Entidad | Campos principales |
|---|---|
| `UnidadAutonoma` | id, posicion_x, posicion_y, altitud, velocidad, estado, bateria, modo, direccion, waypoint, trayectoria, señal_activa |
| `Waypoint` | id, x, y, altitud_objetivo, tipo |
| `ZonaVigilancia` | centro_x, centro_y, radio o límites, nombre |
| `Alerta` | id, tipo, severidad, descripcion, unidad_id, timestamp, activa |
| `EstadoSimulacion` | tiempo_actual, en_ejecucion, pausada, modo_global, delta_t |
| `ConfiguracionSistema` | velocidad_max, radio_vigilancia, separacion_minima, umbral_bateria, tasa_actualizacion |
| `EventoSimulado` | tipo, unidad_id, datos, timestamp |

## 10. Variables del sistema

### 10.1 Variables visibles principales
| Variable | Uso |
|---|---|
| Identificador de unidad | Diferenciación visual y operacional |
| Posición X/Y | Ubicación en el plano |
| Altitud simulada | Dimensión operacional básica |
| Velocidad | Magnitud de desplazamiento |
| Estado | Activo, patrullando, detenido, alerta, fuera de zona |
| Batería simulada | Recurso operacional |
| Distancia al objetivo | Seguimiento de cumplimiento |
| Modo operativo | Contexto funcional |
| Alerta activa | Atención inmediata del operador |
| Última actualización | Referencia temporal |

### 10.2 Variables internas
| Variable | Uso |
|---|---|
| Vector de dirección | Orientación de movimiento |
| Error de posición | Diferencia entre objetivo y posición actual |
| Separación mínima | Prevención de proximidad excesiva |
| Tiempo de actualización | Paso temporal de simulación |
| Radio de vigilancia | Restricción espacial |
| Waypoint asignado | Meta de navegación |
| Historial de trayectoria | Visualización y análisis |
| Estado de señal | Simulación de conectividad |
| Velocidad máxima | Saturación del controlador |

## 11. Algoritmo de simulación

### 11.1 Ciclo propuesto
1. Leer estado actual de la simulación.
2. Para cada unidad, verificar si tiene objetivo o patrón de patrullaje.
3. Calcular error hacia objetivo.
4. Aplicar algoritmo de control.
5. Actualizar posición y variables derivadas.
6. Consumir batería simulada según tiempo y movimiento.
7. Verificar límites de zona y separación.
8. Generar alertas si corresponde.
9. Actualizar trayectoria histórica.
10. Refrescar interfaz y paneles.

### 11.2 Frecuencia sugerida
- Entre **5 Hz y 10 Hz** para el prototipo.
- Suficiente para sensación de tiempo real sin sobrecargar el sistema.

## 12. Algoritmo de control

### 12.1 Recomendación
Usar **control proporcional simple (P)**, no PID como base.

### 12.2 Justificación
Para esta tesis, el objetivo no es demostrar control industrial avanzado, sino un **sistema de monitoreo y control básico, claro y defendible**. El control proporcional:

- Es más fácil de explicar en la defensa.
- Permite calcular error y respuesta de manera directa.
- Es suficiente para navegación 2D hacia waypoints.
- Reduce complejidad matemática y de ajuste.

### 12.3 Lógica propuesta
- Error: diferencia entre posición objetivo y posición actual.
- Dirección: normalización del vector error.
- Velocidad deseada: proporcional a la distancia.
- Saturación: limitar a velocidad máxima.
- Si la unidad está cerca del objetivo, reducir velocidad.
- Si otra unidad invade la separación mínima, aplicar corrección de evasión.
- Si sale de la zona, aplicar corrección hacia el centro o borde seguro.

### 12.4 Cuándo considerar PID
Solo como mejora futura si se desea:

- Movimientos más suaves.
- Control de altitud más refinado.
- Estudio comparativo entre estrategias de control.

## 13. Lógica de alertas
| Alerta | Condición |
|---|---|
| Unidad fuera del área | Posición fuera de límites de la zona estratégica |
| Batería baja | Batería menor al umbral definido |
| Proximidad | Distancia entre dos unidades menor a separación mínima |
| Pérdida simulada de señal | Bandera de señal inactiva durante intervalo definido |
| Objetivo alcanzado | Distancia al waypoint menor a tolerancia |
| Anomalía de movimiento | Velocidad nula prolongada o trayectoria inconsistente |

Las alertas deben tener al menos:

- Tipo.
- Unidad asociada.
- Hora.
- Severidad.
- Estado activa/resuelta.

## 14. Diseño propuesto de la interfaz

### 14.1 Distribución recomendada
| Zona | Contenido |
|---|---|
| Centro | Radar 2D principal |
| Panel izquierdo o derecho | Información detallada de unidad seleccionada |
| Panel inferior o lateral | Controles de simulación y operaciones |
| Barra superior | Estado global, modo activo, hora simulada |
| Barra inferior | Mensajes del sistema y alertas recientes |

### 14.2 Características visuales
- Fondo oscuro tipo centro de monitoreo.
- Líneas en verde/cian tenue.
- Unidades por color según estado.
- Trayectorias semitransparentes.
- Waypoints con íconos simples.
- Barrido radar opcional como elemento visual, no imprescindible para la lógica.

## 15. Modos operativos simulados
| Modo | Descripción |
|---|---|
| Defensivo | Las unidades patrullan y supervisan el perímetro de una zona estratégica. |
| Reconocimiento | Las unidades avanzan hacia puntos de observación o supervisión predefinidos. |
| Mixto o híbrido | Un subconjunto patrulla mientras otro realiza reconocimiento. |

Recomendación académica: usar **reconocimiento** como término principal.

Si el documento institucional exige “ofensivo simulado/no letal”, redefinirlo formalmente como **avance hacia punto de reconocimiento sin representar daño**.

## 16. Flujo de uso del sistema
1. Iniciar aplicación.
2. Configurar parámetros globales.
3. Crear o cargar conjunto inicial de unidades.
4. Seleccionar modo operativo.
5. Asignar waypoints si aplica.
6. Iniciar simulación.
7. Supervisar radar, estados y alertas.
8. Ajustar velocidad, altitud o destino.
9. Pausar o reiniciar.
10. Guardar sesión o exportar resultados si esa función se incluye.

## 17. Requerimientos funcionales
| Código | Requerimiento |
|---|---|
| RF-01 | El sistema debe permitir visualizar una interfaz tipo radar. |
| RF-02 | El sistema debe permitir crear múltiples unidades autónomas simuladas. |
| RF-03 | El sistema debe mostrar la posición de cada unidad. |
| RF-04 | El sistema debe actualizar el movimiento en tiempo real simulado. |
| RF-05 | El sistema debe permitir asignar un objetivo a una unidad. |
| RF-06 | El sistema debe calcular la distancia entre la unidad y su objetivo. |
| RF-07 | El sistema debe mostrar el estado operativo de cada unidad. |
| RF-08 | El sistema debe emitir alertas por batería baja, salida de zona o proximidad. |
| RF-09 | El sistema debe permitir seleccionar modos operativos: defensivo, reconocimiento y mixto. |
| RF-10 | El sistema debe permitir iniciar, pausar y reiniciar la simulación. |
| RF-11 | El sistema debe mostrar trayectoria histórica por unidad. |
| RF-12 | El sistema debe permitir cambiar velocidad y altitud simulada. |
| RF-13 | El sistema debe permitir eliminar unidades del escenario. |
| RF-14 | El sistema debe resaltar visualmente la unidad seleccionada. |
| RF-15 | El sistema debe mostrar alertas activas y eventos recientes en pantalla. |

## 18. Requerimientos no funcionales
| Código | Requerimiento |
|---|---|
| RNF-01 | Interfaz clara y comprensible. |
| RNF-02 | Código modular. |
| RNF-03 | Fácil mantenimiento. |
| RNF-04 | Simulación local sin dependencia de hardware real. |
| RNF-05 | Bajo consumo de recursos. |
| RNF-06 | Posibilidad de expansión futura. |
| RNF-07 | Separación entre lógica de simulación e interfaz gráfica. |
| RNF-08 | Tiempo de respuesta visual adecuado para interacción fluida. |
| RNF-09 | Configuración editable de parámetros principales. |
| RNF-10 | Diseño reproducible y defendible académicamente. |

## 19. Casos de uso principales
- Crear unidad autónoma.
- Seleccionar unidad.
- Asignar waypoint.
- Cambiar modo operativo.
- Iniciar simulación.
- Pausar simulación.
- Reiniciar escenario.
- Modificar velocidad/altitud.
- Supervisar alertas.
- Consultar estado detallado de una unidad.

## 20. Estructura de carpetas propuesta
```text
tesis_simulador/
├─ main.py
├─ app/
│  ├─ ui/
│  ├─ controllers/
│  ├─ views/
│  ├─ widgets/
│  ├─ domain/
│  ├─ simulation/
│  ├─ alerts/
│  ├─ models/
│  ├─ services/
│  ├─ infrastructure/
│  └─ utils/
├─ assets/
│  ├─ icons/
│  └─ styles/
├─ config/
├─ data/
├─ docs/
├─ tests/
└─ requirements.txt
```

## 21. Fases de desarrollo
| Fase | Objetivo |
|---|---|
| F1 | Definición de alcance, variables y arquitectura |
| F2 | Prototipo visual del radar |
| F3 | Motor básico de simulación |
| F4 | Control proporcional y navegación |
| F5 | Alertas y estados |
| F6 | Modos operativos |
| F7 | Persistencia/reportes opcionales |
| F8 | Pruebas, documentación y preparación para defensa |

## 22. Plan de implementación por etapas
1. Diseñar arquitectura y modelo de datos.
2. Construir la interfaz base con radar y paneles.
3. Implementar creación y visualización de unidades.
4. Agregar motor de simulación con actualización temporal.
5. Incorporar waypoints y movimiento controlado.
6. Añadir panel de control y acciones del operador.
7. Implementar alertas y severidades.
8. Integrar modos operativos.
9. Agregar configuración, guardado o exportación si se decide.
10. Probar escenarios y documentar resultados.

## 23. Riesgos técnicos y cómo mitigarlos
| Riesgo | Mitigación |
|---|---|
| Interfaz sobrecargada | Limitar variables visibles a las esenciales |
| Acoplamiento entre GUI y lógica | Separar capas desde el inicio |
| Simulación poco fluida | Ajustar frecuencia de actualización y cantidad de elementos gráficos |
| Control inestable | Usar control proporcional con saturación y tolerancias |
| Alcance excesivo | Priorizar prototipo funcional antes de extras |
| Complejidad visual del radar | Empezar con radar estático y agregar barrido después |
| Falta de defendibilidad | Mantener variables y algoritmos simples, medibles y justificables |

## 24. Qué partes se pueden dejar como futuras mejoras
- Persistencia completa en base de datos.
- Exportación de reportes PDF/CSV.
- Reproducción de sesiones.
- Integración con mapas o capas georreferenciadas.
- Simulación 3D.
- Comparación entre control P, PI o PID.
- Comunicación entre unidades.
- IA básica para patrullaje autónomo avanzado.
- Panel de estadísticas temporales con PyQtGraph.

## 25. Cómo este desarrollo se alinea con la tesis
El sistema propuesto se alinea directamente con el título y propósito de la tesis porque:

- Representa **tecnologías autónomas** en un **entorno simulado**.
- Utiliza una **interfaz gráfica tipo radar** como núcleo del monitoreo.
- Integra **control básico**, no solo visualización.
- Se enfoca en **defensa, vigilancia, supervisión y reconocimiento**, evitando contenidos no apropiados.
- Es técnicamente realizable por estudiantes y defendible como prototipo académico.
- Permite demostrar diseño de software, simulación, control y arquitectura modular en un solo proyecto.

## Recomendación final de enfoque
La versión más sólida para la tesis es un **simulador de escritorio en Python con PySide6**, con radar 2D en `QGraphicsView`, control proporcional simple, alertas básicas y tres modos operativos. Ese alcance ofrece un equilibrio correcto entre **valor académico, factibilidad técnica, calidad visual y tiempo de desarrollo**.

## Preguntas de validación antes de programar
1. ¿Cuántas unidades autónomas deseas manejar en la primera versión: 5, 10, 20 u otra cantidad?
2. ¿Confirmas como tecnología definitiva `Python + PySide6 + QGraphicsView`, o deseas evaluar `PyQt6`?
3. ¿Cuáles variables visibles quieres dejar obligatorias en pantalla y cuáles solo al seleccionar una unidad?
4. ¿Los modos operativos finales serán `defensivo`, `reconocimiento` y `mixto`, o deseas conservar otro nombre institucional?
5. ¿El alcance del prototipo será solo simulación visual con control básico, o incluirá guardado de sesiones?
6. ¿Deseas que el sistema almacene datos de eventos y trayectorias, o solo funcione en memoria?
7. ¿Necesitas exportar reportes académicos o capturas de resultados para la tesis?
8. ¿Quieres que la batería simulada influya solo en alertas, o también limite velocidad/comportamiento?
9. ¿El radar representará una zona circular, rectangular o ambas opciones configurables?
10. ¿Deseas que cada unidad tenga comportamiento individual manual, o también roles automáticos por modo operativo?
