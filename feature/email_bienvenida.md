# Especificación de Comunicación: Email de Bienvenida - ContraVento

**Proyecto:** ContraVento  
**Objetivo:** Confirmar el registro, dar la bienvenida a la comunidad y reforzar los valores de la marca.  
**Tono:** Inspirador, místico, humano y ético.

---

## 1. Configuración del Envío
* **Disparador (Trigger):** Registro exitoso en el formulario de la Landing Page.
* **Tiempo de envío:** Inmediato (0 minutos).
* **Remitente:** Comunidad ContraVento <hola@contravento.com>
* **Formato sugerido:** HTML enriquecido (estética editorial, no solo texto plano).

---

## 2. Elementos Visuales del Correo
* **Fondo del correo:** `#F9F7F2` (Crema orgánico, coherente con la web).
* **Tipografía:** Serif para el saludo y Sans Serif para el cuerpo.
* **Imagen de cabecera:** Una fotografía de detalle (ej. una mano sobre un manillar, un paisaje rural desenfocado o el logo de ContraVento en trazo artesanal).

---

## 3. Cuerpo del Correo (Copywriting)

**Asunto:** Bienvenido a la ruta, {{nombre}}. El camino comienza aquí.

**Preheader:** Al registrarte, has aceptado un pacto con el territorio y la comunidad.

---

**Hola, {{nombre}}.**

Gracias por unirte a **ContraVento**.

Al registrarte, no solo te has unido a una plataforma; has aceptado un pacto con el territorio y con los que, como tú, entienden que pedalear es una forma de habitar el mundo, no de conquistarlo.

En un mundo que nos empuja a ir cada vez más rápido, en ContraVento celebramos al que se detiene. Celebramos al que saluda al paisano, al que consume en la tienda del pueblo y al que deja el camino un poco mejor de como lo encontró.

**¿Qué sigue ahora?**

Mientras terminamos de preparar las herramientas de conexión para tu próxima ruta, te invitamos a llevar estos principios en tu próxima salida:

* **Mira más allá del GPS:** Descubre ese pequeño comercio local que da vida al pueblo.
* **Cuida a la comunidad:** Si ves algo que un compañero deba saber, prepárate para compartirlo.
* **No dejes rastro:** Que lo único que quede de tu paso sea una buena historia.

Muy pronto recibirás noticias nuestras con las primeras rutas y puntos de impacto que estamos mapeando juntos. 

Gracias por pedalear con propósito. Nos vemos en el camino, a favor del viento.

**El equipo de ContraVento** *El camino es el destino.*

---

## 4. Footer del Email
* **Enlace de interés:** [Leer nuestro Manifiesto completo]
* **Redes Sociales:** Instagram (enfocado en fotografía de paisaje y comunidad).
* **Aviso Legal:** Texto de desuscripción y política de privacidad.

---

## 5. Notas Técnicas (Dev)
* Asegurar que el campo `{{nombre}}` tenga un valor por defecto (ej. "Ciclista") en caso de que el usuario no lo proporcione.
* Botones de redes sociales en color `#1B2621` (Verde bosque).