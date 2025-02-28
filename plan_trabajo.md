# Plan de Trabajo: Restauración del CV Assistant

## 1. Diagnóstico Inicial
- [x] Identificar puntos de fallo principales:
  - Ciclos infinitos en certificaciones
  - No se genera el CV al final
  - Estado confuso entre collected_data y atributos directos
  - Transiciones de estado inconsistentes

## 2. Simplificación del Estado (Fase 1)
- [ ] Limpiar ConversationState
  ```python
  class ConversationState:
      def __init__(self):
          self.stage = ConversationStage.START
          self.personal_info = {}
          self.education = []
          self.experience = []
          self.skills = []
          self.languages = []
          self.certifications = []
  ```
- [ ] Eliminar collected_data y current_section_data
- [ ] Verificar que todos los métodos usen los atributos directos

## 3. Flujo de Conversación (Fase 2)
- [ ] Definir transiciones claras:
  1. START -> CONTACT: Al recibir nombre
  2. CONTACT -> EDUCATION: Al recibir contacto
  3. EDUCATION -> EXPERIENCE: Al recibir educación
  4. EXPERIENCE -> SKILLS: Al recibir experiencia
  5. SKILLS -> LANGUAGES: Al recibir habilidades
  6. LANGUAGES -> CERTIFICATIONS: Al recibir idiomas
  7. CERTIFICATIONS -> COMPLETE: Al recibir "no hay más"

- [ ] Implementar comandos de control:
  - "siguiente" o "continuar": Avanza a la siguiente sección
  - "no hay más": Finaliza certificaciones y genera CV

## 4. Generación de CV (Fase 3)
- [ ] Simplificar _generate_cv_html:
  - Usar atributos directos del estado
  - Manejar casos nulos
  - Mejorar formato HTML
  - Agregar mejor manejo de errores

## 5. Pruebas Incrementales
1. [ ] Probar flujo básico:
   ```
   - Nombre -> Alex
   - Contacto -> alex@email.com, 123456789
   - Educación -> Ingeniería, Universidad XYZ, 2020
   - Experiencia -> Desarrollador, Empresa ABC, 2020-2023
   - Habilidades -> Python, JavaScript, AI
   - Idiomas -> Español nativo, Inglés avanzado
   - Certificaciones -> No hay más
   ```

2. [ ] Probar comandos de control:
   ```
   - "siguiente" en cada sección
   - "no hay más" en certificaciones
   ```

3. [ ] Verificar generación de CV:
   - HTML generado correctamente
   - Todos los datos incluidos
   - Formato adecuado

## 6. Mejoras de UX (Fase 4)
- [ ] Mensajes más claros y directos
- [ ] Mejor feedback al usuario
- [ ] Instrucciones más claras para cada sección

## 7. Documentación
- [ ] Actualizar docstrings
- [ ] Documentar flujo de conversación
- [ ] Documentar estructura de datos

## Reglas de Implementación
1. No modificar múltiples fases a la vez
2. Probar cada cambio antes de avanzar
3. Mantener registro de errores encontrados
4. Documentar cada cambio realizado

## Prioridades
1. Estado y flujo básico (Fases 1 y 2)
2. Generación de CV (Fase 3)
3. Pruebas completas
4. Mejoras de UX (Fase 4)

## Métricas de Éxito
- Completar un CV en menos de 5 minutos
- Sin ciclos infinitos
- CV generado correctamente
- Transiciones claras entre estados
