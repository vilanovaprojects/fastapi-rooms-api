# ✅ Checklist: Adaptación de Prompt a tu Entidad

**Instrucciones:** Marca cada casilla `[x]` conforme completes cada tarea.

---

## 1️⃣ Preparación Inicial
- [x] Definir nombre de la entidad
- [x] Listar atributos y tipos de datos
- [x] Identificar restricciones y validaciones
- [x] Planificar relaciones con otras entidades

## 2️⃣ Configuración Base
- [x] Cambiar nombre de entidad en todos los archivos
- [x] Crear estructura de carpetas
- [x] Configurar base de datos (SQLite/PostgreSQL)
- [x] Instalar dependencias (`pip install -r requirements.txt`)

## 3️⃣ Modelo de Datos (SQLAlchemy)
- [x] Actualizar atributos en el modelo
- [x] Crear índices en campos búsqueda
- [ ] Definir relaciones (FK, muchos-a-muchos)
- [x] Validar tipos de datos en BD

## 4️⃣ Esquemas de Validación (Pydantic)
- [x] Crear validadores Pydantic específicos
- [x] Implementar validadores custom
- [ ] Documentar ejemplos en `json_schema_extra`
- [x] Testear validación con datos inválidos

## 5️⃣ Capa de Repositorio
- [x] Implementar métodos CRUD completos
- [x] Manejar excepciones de integridad
- [x] Optimizar queries (select específicos)
- [x] Testear repositorio aisladamente

## 6️⃣ Capa de Servicio
- [x] Implementar lógica de negocio
- [ ] Agregar autenticación/autorización
- [x] Manejar errores y excepciones
- [x] Implementar logging

## 7️⃣ Rutas (FastAPI Endpoints)
- [x] Crear GET all con paginación
- [x] Crear GET by ID
- [x] Crear POST
- [x] Crear PUT
- [x] Crear DELETE
- [x] Documentar con docstrings

## 8️⃣ Criterios de Aceptación (Gherkin)
- [x] Escribir criterios Gherkin
- [x] Cubrir casos exitosos
- [x] Cubrir casos de error
- [x] Cubrir validaciones
- [x] Cubrir casos límite (edge cases)

## 9️⃣ Testing
- [x] Crear tests unitarios del servicio
- [x] Crear tests del repositorio
- [x] Crear tests de integración (routes)
- [x] Implementar fixtures
- [x] Alcanzar +80% cobertura

## 🔟 Documentación y Validación
- [x] Documentar endpoints en OpenAPI
- [x] Validar manualmente en Swagger (`/docs`)
- [x] Ejecutar suite de tests (`pytest -v`)
- [x] Generar reporte de cobertura
- [x] Crear README.md

## 1️⃣1️⃣ Mejoras Adicionales
- [ ] Agregar autenticación JWT
- [x] Implementar logging estructurado
- [ ] Crear Dockerfile
- [ ] Configurar migrations (Alembic)
- [ ] Agregar paginación avanzada

## 1️⃣2️⃣ Despliegue
- [ ] Deployar en servidor (Heroku/AWS/Azure)
- [ ] Testear en producción
- [ ] Configurar CI/CD (GitHub Actions)
- [ ] Monitoreo y alertas
- [ ] Documentación para mantenimiento
