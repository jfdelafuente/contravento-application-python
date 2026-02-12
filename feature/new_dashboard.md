# Especificación Técnica: Dashboard ContraVento

**Descripción:** Panel de control principal para el usuario de la Red Ciclista ContraVento. El diseño prioriza la conexión territorial, la comunidad y la facilidad de uso en entornos de escritorio y tablet.

---

## 1. Arquitectura de Navegación (Header)
La cabecera es fija (sticky) y actúa como el centro de control global.

* **Logo de la app:** Alineado a la izquierda. Enlace directo a la vista de inicio del dashboard.
* **Buscador rápido:** Barra central para búsqueda de usuarios, rutas o pueblos específicos.
* **Notificaciones:** Icono con contador para alertas de seguridad, interacciones sociales y actualizaciones de retos.
* **Avatar de usuario:** Previsualización de la foto de perfil.
* **Botón Perfil:** Acceso al área personal y configuración de privacidad.

---

## 2. Layout del Cuerpo Principal (Main)
Se utiliza un sistema de rejilla (Grid) de tres columnas con pesos específicos para jerarquizar la información.

| Columna | Ancho (%) | Componentes Incluidos |
| :--- | :--- | :--- |
| **Izquierda** | 30% | `SocialStatsCard`, `StatsCard`, `ActiveChallengesCard`, `AchievementCard` |
| **Central** | 50% | `ActivityFeed`, `SuggestedRoutes` |
| **Derecha** | 20% | `QuickActions`, `ActiveFriendsCard`, `BikeEquipmentCard` |

### Detalle de Componentes por Columna

#### Columna Izquierda: Perfil y Progreso
1.  **`<SocialStatsCard>`**: Visualización de métricas de comunidad (Seguidores y Seguidos).
2.  **`<StatsCard>`**: Estadísticas personales (km recorridos, pueblos visitados, impacto económico local estimado).
3.  **`<ActiveChallengesCard>`**: Desafíos actuales del usuario (ej. "Ruta de los Molinos", "Visita 5 comercios rurales").
4.  **`<AchievementCard>`**: Carrusel o lista de insignias y logros obtenidos por comportamiento ético y exploración.

#### Col