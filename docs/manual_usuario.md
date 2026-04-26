# Manual de Usuario

## 1. Objetivo del manual
Este manual explica cómo usar el sistema de forma práctica, paso a paso, como si fuera una guía de operación.

La idea es responder a una pregunta simple:

**¿Qué debo hacer exactamente para usar el sistema correctamente?**

---

## 2. Antes de comenzar

Cuando abras la aplicación verás dos ventanas:

- **Radar Operativo**
- **Centro de Control**

La ventana principal para observar es el radar.  
La ventana principal para tomar acciones es el Centro de Control.

---

## 3. Flujo básico de uso

## Paso 1. Abrir la aplicación

1. Ejecuta el sistema.
2. Espera a que aparezcan las dos ventanas.
3. Verifica que el Radar Operativo y el Centro de Control estén visibles.

### Qué debes observar
- el radar vacío o con estado inicial;
- la pestaña `Estado` en el Centro de Control;
- el mensaje general de sistema listo.

---

## Paso 2. Seleccionar un escenario

1. Ve a la pestaña `Control` en el Centro de Control.
2. Busca el selector `Escenario`.
3. Haz clic sobre el escenario que quieres usar.

### Qué ocurre
Se abrirá la ventana **Configurar escenario**.

---

## Paso 3. Configurar el escenario

En la ventana `Configurar escenario` debes revisar estos campos:

- cantidad de unidades;
- número de enjambres;
- distribución;
- usar unidades existentes o reemplazar unidades;
- velocidad máxima;
- altitud objetivo;
- radio de vigilancia;
- separación mínima;
- umbral de batería baja;
- iniciar simulación automáticamente.

### Recomendación práctica
Si estás haciendo una demostración sencilla:

- usa 6 unidades;
- usa 2 enjambres en escenario combinado;
- deja la distribución en `Mitad y mitad`;
- no actives inicio automático si quieres explicar primero.

### Cómo aplicar
1. Revisa los valores.
2. Haz clic en `Aplicar escenario`.

### Cómo cancelar
Si no quieres cambiar nada:

1. Haz clic en `Cancelar`.

---

## Paso 4. Observar el radar

Después de aplicar el escenario:

1. Mira la ventana `Radar Operativo`.
2. Verifica:
   - la zona estratégica;
   - los puntos de observación;
   - las unidades;
   - las etiquetas como `U01 [E1-P]`.

### Qué significa cada etiqueta
- `U01`: unidad 1
- `E1`: Enjambre 1
- `P`: patrullaje

Si ves `R`, significa reconocimiento.  
Si ves `T`, significa tarea temporal.  
Si ves `M`, significa control manual.

---

## Paso 5. Iniciar la simulación

1. Ve al Centro de Control.
2. En la pestaña `Control`, haz clic en `Iniciar`.

### Qué ocurre
- las unidades comienzan a moverse;
- el tiempo de simulación avanza;
- el radar empieza a mostrar la operación en ejecución.

---

## Paso 6. Seleccionar una unidad

1. Ve al Radar Operativo.
2. Haz clic sobre una unidad.

### Qué ocurre
- la unidad queda seleccionada;
- en la pestaña `Estado` aparece su información detallada.

### Qué puedes revisar
- ID;
- enjambre;
- rol de enjambre;
- rol actual;
- tarea;
- posición;
- velocidad;
- batería;
- estado;
- distancia al objetivo.

---

## Paso 7. Asignar un objetivo manual

### Opción A. Tarea temporal
Usa esta opción si quieres que la unidad vaya a un punto y luego vuelva a su misión original.

1. Selecciona una unidad en el radar.
2. Ve al Centro de Control.
3. En la pestaña `Control`, en `Asignación manual`, elige `Tarea temporal`.
4. Haz clic en `Asignar objetivo`.
5. Ahora vuelve al radar.
6. Haz clic en el punto donde quieres enviar la unidad.

### Qué ocurre
- la unidad cambia temporalmente su tarea;
- va al punto indicado;
- al terminar, regresa a su misión original.

### Opción B. Control manual
Usa esta opción si quieres que la unidad deje su misión automática.

1. Selecciona una unidad.
2. En `Asignación manual`, elige `Control manual`.
3. Haz clic en `Asignar objetivo`.
4. Haz clic en un punto del radar.

### Qué ocurre
- la unidad pasa a control manual;
- ya no sigue automáticamente la misión anterior.

---

## Paso 8. Cambiar el modo operativo

1. Ve a la pestaña `Control`.
2. Busca `Modo operativo`.
3. Elige uno de estos:
   - Defensivo
   - Reconocimiento
   - Mixto

### Qué ocurre
- las unidades existentes cambian su comportamiento;
- no se crean unidades nuevas;
- el sistema reaplica la lógica del modo sobre las unidades actuales.

### Importante
Si no hay unidades activas, el sistema mostrará un mensaje indicando que primero debes crear unidades o cargar un escenario.

---

## Paso 9. Ajustar parámetros

1. Ve a la pestaña `Parámetros`.
2. Ajusta los valores que necesites.

### Qué puedes cambiar
- velocidad máxima;
- altitud;
- separación mínima;
- radio de vigilancia;
- batería baja;
- unidades activas;
- sonido de alertas.

### Qué pasa al cambiar parámetros
Los cambios se aplican al comportamiento general del sistema sin necesidad de cerrar la aplicación.

---

## Paso 10. Revisar alertas

1. Ve a la pestaña `Alertas`.
2. Observa el listado de mensajes.

### Qué debes interpretar
- `INFO`: información;
- `WARN`: advertencia;
- `CRIT`: alerta crítica.

### Qué contienen las alertas
- hora;
- unidad afectada;
- enjambre si aplica;
- descripción del evento.

### Si quieres limpiar el panel
Haz clic en `Limpiar alertas`.

---

## Paso 11. Pausar la simulación

1. Ve a la pestaña `Control`.
2. Haz clic en `Pausar`.

### Qué ocurre
- las unidades dejan de avanzar;
- el tiempo operativo se detiene;
- puedes revisar la situación sin cambios.

---

## Paso 12. Reiniciar la simulación

1. Ve a la pestaña `Control`.
2. Haz clic en `Reiniciar`.

### Qué ocurre
- la simulación vuelve a un estado inicial del escenario actual;
- se restablece la estructura operativa;
- las unidades recuperan la misión general del escenario.

---

## 4. Uso recomendado para una demostración

Si vas a mostrar el sistema en una exposición, sigue este orden:

1. abre la aplicación;
2. elige `Vigilancia y reconocimiento combinado`;
3. configura 6 unidades y 2 enjambres;
4. aplica el escenario;
5. inicia la simulación;
6. explica el radar;
7. selecciona una unidad;
8. asigna una tarea temporal;
9. muestra el panel de alertas;
10. pausa y explica el estado global.

---

## 5. Consejos de uso

- No cambies demasiados parámetros al mismo tiempo durante la defensa.
- Usa primero un escenario claro antes de pasar a controles manuales.
- Explica siempre la diferencia entre escenario, modo, enjambre y unidad.
- Si vas a demostrar control manual, hazlo con una sola unidad para que sea fácil de seguir.

---

## 6. Resumen práctico

Si quieres resumir el uso en una sola secuencia:

1. selecciona escenario;
2. configura;
3. aplica;
4. inicia;
5. observa el radar;
6. selecciona una unidad;
7. asigna objetivo si hace falta;
8. revisa alertas;
9. pausa o reinicia.
