# Especificación Técnica: Integración de Redes Sociales y Privacidad - ContraVento

**Concepto:** Los enlaces sociales son "puentes" opcionales que se activan según el nivel de confianza y los permisos de seguridad del usuario.

---

## 1. Configuración de Enlaces Sociales
El usuario podrá añadir los siguientes enlaces en su perfil, definiendo para cada uno su nivel de visibilidad:

| Red Social | Tipo de Enlace | Propósito en ContraVento |
| :--- | :--- | :--- |
| **Instagram** | URL / @usuario | Compartir la mirada visual del viaje. |
| **Substack / Blog** | URL | Compartir crónicas y relatos profundos. |
| **Strava** | URL / @usuario | Para ciclista que subes sus rutas. |
| **Portfolio** | URL | Para fotógrafos, artistas o guías locales. |

---

## 2. Matriz de Privacidad de Enlaces
A diferencia de otras redes, ContraVento permite granularidad total. El usuario elige quién ve cada icono:

* **Nivel: Público (Todo el mundo)**
    * Cualquier visitante o usuario de la plataforma puede ver el enlace.
    * *Uso recomendado:* Para perfiles que buscan visibilidad como guías o creadores de contenido rural.

* **Nivel: Solo Comunidad (Usuarios Registrados)**
    * Solo visible para quienes han aceptado el Manifiesto de ContraVento.
    * *Uso recomendado:* Para mantener la privacidad fuera de buscadores como Google.

* **Nivel: Círculo de Confianza (Seguidores Mutuos)**
    * Solo visible si ambos usuarios se siguen.
    * *Uso recomendado:* Redes personales o apps de mensajería (WhatsApp/Telegram).

* **Nivel: Oculto**
    * El enlace se guarda en la base de datos pero no se muestra en el perfil público.

---

## 3. Lógica de Interfaz (UI/UX)
1. **Iconografía Coherente:** Los iconos sociales deben adaptarse a la estética de ContraVento (tonos tierra, trazos suaves) para no romper la armonía visual.
2. **Indicador de Privacidad:** Junto a cada enlace en la edición de perfil, aparecerá un icono de candado o un ojo tachado que indique el nivel de visibilidad actual.
3. **El "Botón de Contacto Seguro":** Si un usuario tiene su Telegram en nivel "Seguidores", los extraños verán un botón que dice: *"Sigue a este ciclista para ver sus redes de contacto"*.

---

## 4. Seguridad de Datos
* **Sanitización:** Todos los enlaces externos serán validados y pasarán por un "Proxy de seguridad" para evitar ataques de phishing.
* **Atributo `rel="me nofollow"`:** Para proteger el SEO del usuario y cumplir con estándares de identidad descentralizada.