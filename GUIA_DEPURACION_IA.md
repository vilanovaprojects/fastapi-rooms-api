# 🔧 GUÍA DE DEPURACIÓN Y REPARACIÓN DE TESTS CON IA

## Índice
1. [Introducción](#introducción)
2. [Prompt 1: Mock incorrecto](#prompt-1-mock-incorrecto)
3. [Prompt 2: Aserción incorrecta](#prompt-2-aserción-incorrecta)
4. [Prompt 3: Error en código fuente](#prompt-3-error-en-código-fuente)
5. [Prompt 4: Reparación en lote](#prompt-4-reparación-en-lote)
6. [Rúbrica de evaluación](#rúbrica-de-evaluación)

---

## Introducción

En un flujo de **ALM generativo**, la generación de software no termina cuando se escribe código o se crean tests. El ciclo real es:

```
generar → testear → fallar → diagnosticar → corregir → repetir
```

Este bucle de **auto-reparación** es una de las capacidades más potentes de la IA aplicada al desarrollo. Cuando un agente ejecuta una suite de tests y encuentra errores, analiza el fallo, infiere la causa raíz, propone una corrección y vuelve a ejecutar los tests.

**Objetivo del alumnado**: practicar exactamente ese patrón usando la IA como asistente de diagnóstico y reparación.

La habilidad clave es distinguir entre:
- **test defectuoso** (mock incorrecto, aserción equivocada),
- **implementación defectuosa** (bug real en el código),
- **entorno defectuoso** (dependencia faltante, configuración incorrecta).

---

# Prompt 1: Mock incorrecto

## Objetivo didáctico
Detectar cuándo un test falla no porque el código esté mal, sino porque el **mock está mal configurado** y no representa correctamente el comportamiento esperado.

## Escenario
En `SalaService.crear_sala()`, el servicio valida primero si ya existe una sala con el mismo nombre y luego delega la creación en el repositorio.

## Código bajo prueba

```python
# app/services/sala_service.py (líneas 81-101)

def crear_sala(self, sala_data: SalaCreate) -> Sala:
    """Crea una nueva sala con validaciones de negocio."""
    self._validar_nombre_unico_para_creacion(sala_data.nombre)

    try:
        return self.repository.crear(sala_data)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
```

## Test fallido

```python
# tests/test_sala_service_mock_fallido.py

import pytest
from unittest.mock import Mock

from app.services.sala_service import SalaService
from app.schemas.sala_schema import SalaCreate


def test_crear_sala_devuelve_objeto_creado():
    """Test con mock incorrecto: obtener_por_nombre devuelve un valor truthy."""
    db = Mock()
    service = SalaService(db)

    service.repository = Mock()
    # ❌ PROBLEMA: devuelve un dict (truthy) en lugar de None
    service.repository.obtener_por_nombre.return_value = {
        "id": 1,
        "nombre": "Aula A-101"
    }
    service.repository.crear.return_value = {
        "id": 2,
        "nombre": "Aula B-201"
    }

    sala_data = SalaCreate(
        nombre="Aula B-201",
        piso=2,
        capacidad=40,
        tipo_sala="Aula"
    )

    resultado = service.crear_sala(sala_data)

    assert resultado["nombre"] == "Aula B-201"
```

## Mensaje de error

```
FAILED tests/test_sala_service_mock_fallido.py::test_crear_sala_devuelve_objeto_creado

fastapi.exceptions.HTTPException: 409: Una sala con el nombre 'Aula B-201' ya existe
```

## Análisis esperado

El problema no está en `crear_sala()`. El fallo proviene de un mock inconsistente:

- `obtener_por_nombre` está devolviendo un dict (truthy),
- El servicio interpreta que la sala ya existe,
- Nunca llega a ejecutar `repository.crear(...)`.
- Lanza una excepción 409 CONFLICT.

Además, el mock devuelve un nombre diferente del que se consulta, evidenciando que el test no representa el comportamiento real del repositorio.

## Prompt para la IA

```
Estás actuando como asistente de depuración de tests en Python con pytest.

Analiza el siguiente test fallido, el mensaje de error y el código del servicio. 
Tu tarea es:

1. Explicar la causa raíz del fallo.
2. Determinar si el error está en el test, en el mock o en el código fuente.
3. Proponer una corrección mínima.
4. Devolver la versión corregida del test.
5. Explicar por qué la corrección es coherente con la lógica de negocio.

**Código del servicio:**

```python
def crear_sala(self, sala_data: SalaCreate) -> Sala:
    self._validar_nombre_unico_para_creacion(sala_data.nombre)
    try:
        return self.repository.crear(sala_data)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
```

**Test fallido:**

```python
import pytest
from unittest.mock import Mock

from app.services.sala_service import SalaService
from app.schemas.sala_schema import SalaCreate


def test_crear_sala_devuelve_objeto_creado():
    db = Mock()
    service = SalaService(db)

    service.repository = Mock()
    service.repository.obtener_por_nombre.return_value = {
        "id": 1,
        "nombre": "Aula A-101"
    }
    service.repository.crear.return_value = {
        "id": 2,
        "nombre": "Aula B-201"
    }

    sala_data = SalaCreate(
        nombre="Aula B-201",
        piso=2,
        capacidad=40,
        tipo_sala="Aula"
    )

    resultado = service.crear_sala(sala_data)

    assert resultado["nombre"] == "Aula B-201"
```

**Error:**

```
fastapi.exceptions.HTTPException: 409: Una sala con el nombre 'Aula B-201' ya existe
```

Devuelve:
- Diagnóstico detallado
- Corrección del test
- Explicación de la lógica
```

## Solución esperada

```python
# tests/test_sala_service_mock_corregido.py

from unittest.mock import Mock

from app.services.sala_service import SalaService
from app.schemas.sala_schema import SalaCreate


def test_crear_sala_devuelve_objeto_creado():
    """Test corregido: mock representa correctamente el comportamiento."""
    db = Mock()
    service = SalaService(db)

    service.repository = Mock()
    # ✅ CORRECCIÓN: obtener_por_nombre devuelve None (no existe la sala)
    service.repository.obtener_por_nombre.return_value = None
    service.repository.crear.return_value = Mock(
        id=2,
        nombre="Aula B-201",
        piso=2,
        capacidad=40,
        tipo_sala="Aula"
    )

    sala_data = SalaCreate(
        nombre="Aula B-201",
        piso=2,
        capacidad=40,
        tipo_sala="Aula"
    )

    resultado = service.crear_sala(sala_data)

    # ✅ Verificar que se llamó a obtener_por_nombre con el nombre correcto
    service.repository.obtener_por_nombre.assert_called_once_with("Aula B-201")
    
    # ✅ Verificar que se llamó a crear con los datos correctos
    service.repository.crear.assert_called_once_with(sala_data)
    
    # ✅ Aserción principal
    assert resultado.nombre == "Aula B-201"
```

---

# Prompt 2: Aserción incorrecta

## Objetivo didáctico
Identificar cuándo el comportamiento real es correcto y el error está en la **expectativa del test**.

## Escenario
El endpoint POST `/api/v1/salas` está correctamente configurado para devolver **201 Created** según está definido en la ruta.

## Código relevante

```python
# app/routes/sala_routes.py (líneas 63-77)

@router.post("", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def crear_sala(
    sala: SalaCreate,
    service: SalaService = Depends(get_sala_service),
) -> SalaResponse:
    """Crea una nueva sala en el sistema.

    Args:
        sala: Datos de la nueva sala.
        service: Servicio de negocio inyectado.

    Returns:
        La sala creada.
    """
    return service.crear_sala(sala)
```

## Test fallido

```python
# tests/test_sala_routes_assert_fallida.py

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_post_sala_devuelve_200():
    """Test con aserción incorrecta: espera 200 en lugar de 201."""
    payload = {
        "nombre": "Aula C-301",
        "piso": 3,
        "capacidad": 20,
        "tipo_sala": "Aula"
    }

    response = client.post("/api/v1/salas", json=payload)

    # ❌ PROBLEMA: el test espera 200, pero la ruta retorna 201
    assert response.status_code == 200
```

## Mensaje de error

```
FAILED tests/test_sala_routes_assert_fallida.py::test_post_sala_devuelve_200

E       assert 201 == 200
E        +  where 201 = <Response [201 Created]>.status_code
```

## Análisis esperado

El test expresa una expectativa **incorrecta**:

- La ruta está correctamente definida con `status_code=status.HTTP_201_CREATED`.
- El contrato HTTP para creación de recursos establece 201 CREATED.
- El endpoint funciona correctamente.
- La aserción del test es incorrecta.

## Prompt para la IA

```
Actúa como experto en depuración de tests para FastAPI y pytest.

Analiza este test fallido y determina si:
- el endpoint está mal implementado,
- o la aserción del test es incorrecta.

Debes:
1. Identificar la causa raíz.
2. Explicar qué contrato HTTP aplica en este caso.
3. Corregir el test con el menor cambio posible.
4. Proponer una mejora adicional para hacer el test más robusto.

**Código de la ruta:**

```python
@router.post("", response_model=SalaResponse, status_code=status.HTTP_201_CREATED)
def crear_sala(sala: SalaCreate, service: SalaService = Depends(get_sala_service)):
    return service.crear_sala(sala)
```

**Test fallido:**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_post_sala_devuelve_200():
    payload = {
        "nombre": "Aula C-301",
        "piso": 3,
        "capacidad": 20,
        "tipo_sala": "Aula"
    }

    response = client.post("/api/v1/salas", json=payload)

    assert response.status_code == 200
```

**Error:**

```
assert 201 == 200
```

Devuelve:
- Diagnóstico
- Contrato HTTP esperado
- Test corregido
- Mejoras adicionales
```

## Solución esperada

```python
# tests/test_sala_routes_assert_corregida.py

from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_post_sala_devuelve_201_created():
    """Test corregido: espera el status code correcto (201 CREATED)."""
    payload = {
        "nombre": "Aula C-301",
        "piso": 3,
        "capacidad": 20,
        "tipo_sala": "Aula"
    }

    response = client.post("/api/v1/salas", json=payload)

    # ✅ CORRECCIÓN: esperar 201 CREATED (no 200 OK)
    assert response.status_code == status.HTTP_201_CREATED

    # ✅ MEJORA: validar que la respuesta contiene datos esperados
    data = response.json()
    assert "id" in data
    assert data["id"] is not None
    assert isinstance(data["id"], int)
    assert data["id"] > 0
    
    # ✅ Validar que los datos corresponden
    assert data["nombre"] == "Aula C-301"
    assert data["piso"] == 3
    assert data["capacidad"] == 20
    assert data["tipo_sala"] == "Aula"
    
    # ✅ Validar que se generaron timestamps
    assert "fecha_creacion" in data
    assert "fecha_actualizacion" in data
```

---

# Prompt 3: Error en código fuente

## Objetivo didáctico
Reconocer cuándo el test está bien y el defecto está en la **implementación del código**.

## Escenario
Se necesita validar que el total de salas filtradas refleje correctamente la consulta. Sin embargo, la implementación actual devuelve el **total global**, no el **total filtrado**.

## Código relevante

```python
# app/services/sala_service.py (líneas 23-59)

def obtener_todas_salas(
    self,
    skip: int = 0,
    limit: int = 10,
    tipo_sala: Optional[str] = None,
    estado: Optional[str] = None,
) -> dict:
    """Obtiene las salas con paginación y filtros opcionales."""
    self._validar_parametros_paginacion(skip=skip, limit=limit)

    salas = self.repository.filtrar(
        skip=skip,
        limit=limit,
        tipo_sala=tipo_sala,
        estado=estado,
    )
    
    # ❌ PROBLEMA: cuenta el total global, no el total filtrado
    total_salas = self.repository.contar_total()

    return {
        "total": total_salas,
        "skip": skip,
        "limit": limit,
        "salas": salas,
    }
```

## Test fallido

```python
# tests/test_sala_service_total_filtrado.py

from unittest.mock import Mock
from app.services.sala_service import SalaService


def test_obtener_salas_filtradas_devuelve_total_filtrado():
    """Test que valida que el total refleja la consulta filtrada."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()

    # Simular: hay 2 laboratorios
    service.repository.filtrar.return_value = [
        {"id": 1, "tipo_sala": "Laboratorio"},
        {"id": 2, "tipo_sala": "Laboratorio"},
    ]
    
    # Pero en total hay 5 salas (de todos los tipos)
    service.repository.contar_total.return_value = 5

    resultado = service.obtener_todas_salas(tipo_sala="Laboratorio")

    # ✅ El test espera que total sea 2 (salas filtradas)
    # ❌ Pero la implementación devuelve 5 (total global)
    assert resultado["total"] == 2
```

## Mensaje de error

```
FAILED tests/test_sala_service_total_filtrado.py::test_obtener_salas_filtradas_devuelve_total_filtrado

E       assert 5 == 2
E        +  where 5 = resultado['total']
```

## Análisis esperado

El test expresa una expectativa razonable y correcta. El campo `total` debe representar el total de elementos que cumplen los filtros, no el total global de la tabla.

Hay un **bug real en la implementación**:
- Se filtran correctamente los datos,
- Pero se cuenta el total de forma incorrecta.
- El usuario recibe información inconsistente.

## Prompt para la IA

```
Actúa como asistente de reparación de software para FastAPI y SQLAlchemy.

Analiza el siguiente test fallido. Tu tarea es decidir si:
- el test está mal planteado,
- o existe un bug real en la implementación.

Debes:
1. Explicar la discrepancia entre comportamiento esperado y comportamiento actual.
2. Inferir la intención funcional más probable.
3. Proponer una corrección del código fuente.
4. Mostrar el fragmento corregido.
5. Explicar las implicaciones de la corrección en la API.

**Código actual:**

```python
def obtener_todas_salas(self, skip=0, limit=10, tipo_sala=None, estado=None):
    self._validar_parametros_paginacion(skip=skip, limit=limit)

    salas = self.repository.filtrar(
        skip=skip,
        limit=limit,
        tipo_sala=tipo_sala,
        estado=estado,
    )
    
    # Cuenta el total de todas las salas
    total_salas = self.repository.contar_total()

    return {
        "total": total_salas,
        "skip": skip,
        "limit": limit,
        "salas": salas,
    }
```

**Test fallido:**

```python
from unittest.mock import Mock
from app.services.sala_service import SalaService

def test_obtener_salas_filtradas_devuelve_total_filtrado():
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()

    service.repository.filtrar.return_value = [
        {"id": 1, "tipo_sala": "Laboratorio"},
        {"id": 2, "tipo_sala": "Laboratorio"},
    ]
    service.repository.contar_total.return_value = 5

    resultado = service.obtener_todas_salas(tipo_sala="Laboratorio")

    # Espera que total sea 2 (salas filtradas)
    assert resultado["total"] == 2
```

**Error:**

```
assert 5 == 2
```

Devuelve:
- Diagnóstico del bug
- Análisis de requisitos
- Corrección del código
- Impacto en la API
```

## Solución esperada

### Opción A: Usar el conteo de resultados paginados (simple)

```python
# app/services/sala_service.py (CORREGIDO)

def obtener_todas_salas(
    self,
    skip: int = 0,
    limit: int = 10,
    tipo_sala: Optional[str] = None,
    estado: Optional[str] = None,
) -> dict:
    """Obtiene las salas con paginación y filtros opcionales.
    
    El campo 'total' representa el número de resultados en esta página.
    """
    self._validar_parametros_paginacion(skip=skip, limit=limit)

    salas = self.repository.filtrar(
        skip=skip,
        limit=limit,
        tipo_sala=tipo_sala,
        estado=estado,
    )
    
    # ✅ CORRECCIÓN: contar solo los resultados filtrados
    total_salas = len(salas)

    return {
        "total": total_salas,
        "skip": skip,
        "limit": limit,
        "salas": salas,
    }
```

### Opción B: Introducir método de conteo con filtros (robusto)

```python
# app/repositories/sala_repository.py (MEJORA)

def contar_filtrado(
    self,
    tipo_sala: Optional[str] = None,
    estado: Optional[str] = None,
) -> int:
    """Cuenta el total de salas que cumplen los filtros."""
    query = self._crear_consulta_filtrada(tipo_sala=tipo_sala, estado=estado)
    return query.count()
```

```python
# app/services/sala_service.py (CORREGIDO - OPCIÓN B)

def obtener_todas_salas(
    self,
    skip: int = 0,
    limit: int = 10,
    tipo_sala: Optional[str] = None,
    estado: Optional[str] = None,
) -> dict:
    """Obtiene las salas con paginación y filtros opcionales."""
    self._validar_parametros_paginacion(skip=skip, limit=limit)

    salas = self.repository.filtrar(
        skip=skip,
        limit=limit,
        tipo_sala=tipo_sala,
        estado=estado,
    )
    
    # ✅ CORRECCIÓN: contar solo los que cumplen los filtros
    total_salas = self.repository.contar_filtrado(
        tipo_sala=tipo_sala,
        estado=estado,
    )

    return {
        "total": total_salas,
        "skip": skip,
        "limit": limit,
        "salas": salas,
    }
```

---

# Prompt 4: Reparación en lote

## Objetivo didáctico
Practicar el diagnóstico y reparación de **múltiples fallos en paralelo**, identificando patrones comunes y diferencias contextuales.

## Escenario
Se ha ejecutado la suite de tests después de un refactor parcial y hay **4 tests fallidos** de diferentes naturalezas. El desafío es diagnosticar todos, categorizarlos y corregirlos eficientemente.

## Suite de tests fallidos

```python
# tests/test_suite_fallida_lote.py

from unittest.mock import Mock, patch
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.services.sala_service import SalaService
from app.schemas.sala_schema import SalaCreate


# ============================================================================
# FALLO 1: Mock incorrecto - respuesta en formato incorrecto
# ============================================================================

def test_crear_sala_mock_response_error():
    """Test 1: Mock devuelve diccionario en lugar de objeto Sala."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    service.repository.obtener_por_nombre.return_value = None
    
    # ❌ PROBLEMA: devuelve dict en lugar de objeto Sala
    service.repository.crear.return_value = {
        "id": 1,
        "nombre": "Aula A-101"
    }

    sala_data = SalaCreate(
        nombre="Aula A-101",
        piso=1,
        capacidad=30,
        tipo_sala="Aula"
    )

    resultado = service.crear_sala(sala_data)
    
    # ❌ Esto falla porque resultado es un dict, no un objeto con atributos
    assert resultado.nombre == "Aula A-101"


# ============================================================================
# FALLO 2: Aserción incorrecta - compara tipos incompatibles
# ============================================================================

def test_obtener_paginacion_skip_limit():
    """Test 2: Aserción compara tipos incompatibles."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    service.repository.filtrar.return_value = [Mock(), Mock(), Mock()]
    service.repository.contar_total.return_value = 10

    resultado = service.obtener_todas_salas(skip=5, limit=3)

    # ❌ PROBLEMA: "skip" es int pero se compara con string
    assert resultado["skip"] == "5"


# ============================================================================
# FALLO 3: Error en código fuente - lógica de validación invertida
# ============================================================================

def test_validar_paginacion_rechaza_limit_cero():
    """Test 3: Espera que limit=0 sea rechazado."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()

    sala_data = SalaCreate(
        nombre="Test",
        piso=1,
        capacidad=20,
        tipo_sala="Aula"
    )

    # ❌ El test espera que limit=0 levante excepción
    # Pero el código permite limit >= 1, así que limit=0 debería fallar
    from fastapi import HTTPException
    
    try:
        resultado = service.obtener_todas_salas(skip=0, limit=0)
        # Si no hay excepción, el test falla
        assert False, "Debería haber levantado HTTPException"
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST


# ============================================================================
# FALLO 4: Aserción múltiple - estructura de respuesta inconsistente
# ============================================================================

def test_obtener_salas_estructura_respuesta():
    """Test 4: La respuesta no contiene todos los campos esperados."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    
    sala_mock = Mock()
    sala_mock.id = 1
    sala_mock.nombre = "Aula A-101"
    sala_mock.piso = 1
    sala_mock.capacidad = 30
    sala_mock.tipo_sala = "Aula"
    sala_mock.numero_ventanas = 4
    sala_mock.tiene_proyector = True
    sala_mock.tiene_aire_acondicionado = True
    sala_mock.estado = "activa"
    sala_mock.descripcion = "Aula de teoría"
    
    service.repository.filtrar.return_value = [sala_mock]
    service.repository.contar_total.return_value = 1

    resultado = service.obtener_todas_salas()

    # ❌ Falla porque espera "resultado" pero la API devuelve "salas"
    assert "resultado" in resultado
    assert len(resultado["resultado"]) == 1
```

## Mensajes de error

```
FAILED tests/test_suite_fallida_lote.py::test_crear_sala_mock_response_error
E       AttributeError: 'dict' object has no attribute 'nombre'

FAILED tests/test_suite_fallida_lote.py::test_obtener_paginacion_skip_limit
E       assert 5 == '5'
E        +  where 5 = resultado['skip']

FAILED tests/test_suite_fallida_lote.py::test_validar_paginacion_rechaza_limit_cero
AssertionError: Debería haber levantado HTTPException

FAILED tests/test_suite_fallida_lote.py::test_obtener_salas_estructura_respuesta
E       KeyError: 'resultado'
```

## Prompt para la IA

```
Actúa como experto en testing y depuración de software.

Se han ejecutado 4 tests y todos fallan. Tu tarea es:

1. Clasificar cada fallo en UNA de estas categorías:
   - A: Mock incorrecto
   - B: Aserción incorrecta
   - C: Bug en código fuente
   - D: Estructura de datos inconsistente

2. Para cada fallo, proporciona:
   - Categoría
   - Causa raíz
   - Responsabilidad (¿quién debe corregir?: test, mock, o código fuente?)

3. Corrige TODOS los tests

4. Si hay bugs en el código fuente, corrígelos también

5. Proporciona una tabla resumen

**Tests fallidos:**

\`\`\`python
# FALLO 1: Mock response error
def test_crear_sala_mock_response_error():
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    service.repository.obtener_por_nombre.return_value = None
    
    service.repository.crear.return_value = {
        "id": 1,
        "nombre": "Aula A-101"
    }

    sala_data = SalaCreate(
        nombre="Aula A-101",
        piso=1,
        capacidad=30,
        tipo_sala="Aula"
    )

    resultado = service.crear_sala(sala_data)
    
    assert resultado.nombre == "Aula A-101"


# FALLO 2: Aserción tipo incompatible
def test_obtener_paginacion_skip_limit():
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    service.repository.filtrar.return_value = [Mock(), Mock(), Mock()]
    service.repository.contar_total.return_value = 10

    resultado = service.obtener_todas_salas(skip=5, limit=3)

    assert resultado["skip"] == "5"


# FALLO 3: Lógica de validación
def test_validar_paginacion_rechaza_limit_cero():
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()

    sala_data = SalaCreate(
        nombre="Test",
        piso=1,
        capacidad=20,
        tipo_sala="Aula"
    )

    from fastapi import HTTPException
    
    try:
        resultado = service.obtener_todas_salas(skip=0, limit=0)
        assert False, "Debería haber levantado HTTPException"
    except HTTPException as e:
        assert e.status_code == status.HTTP_400_BAD_REQUEST


# FALLO 4: Estructura de respuesta
def test_obtener_salas_estructura_respuesta():
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    
    sala_mock = Mock()
    sala_mock.id = 1
    sala_mock.nombre = "Aula A-101"
    
    service.repository.filtrar.return_value = [sala_mock]
    service.repository.contar_total.return_value = 1

    resultado = service.obtener_todas_salas()

    assert "resultado" in resultado
    assert len(resultado["resultado"]) == 1
\`\`\`

**Errores:**

\`\`\`
FAILED test_crear_sala_mock_response_error
E       AttributeError: 'dict' object has no attribute 'nombre'

FAILED test_obtener_paginacion_skip_limit
E       assert 5 == '5'

FAILED test_validar_paginacion_rechaza_limit_cero
AssertionError: Debería haber levantado HTTPException

FAILED test_obtener_salas_estructura_respuesta
E       KeyError: 'resultado'
\`\`\`

Devuelve:
- Tabla clasificatoria
- Causa raíz de cada fallo
- Tests corregidos
- Código fuente corregido (si aplica)
- Explicación de por qué cada corrección resuelve el problema
```

## Soluciones esperadas

### Tabla clasificatoria

| Fallo | Categoría | Causa raíz | Responsabilidad | Severidad |
|-------|-----------|-----------|-----------------|-----------|
| Test 1 | Mock incorrecto | Mock devuelve dict en lugar de objeto Sala | Test | Alta |
| Test 2 | Aserción incorrecta | Compara int con string | Test | Media |
| Test 3 | Bug en código | Validación limit=0 no rechaza | Código | Alta |
| Test 4 | Estructura inconsistente | Test espera "resultado", API devuelve "salas" | Test | Alta |

### Tests corregidos

```python
# tests/test_suite_fallida_corregida.py

from unittest.mock import Mock
from fastapi import status, HTTPException
import pytest

from app.services.sala_service import SalaService
from app.schemas.sala_schema import SalaCreate


# ✅ FALLO 1 - CORREGIDO: Mock debe devolver objeto Sala, no dict
def test_crear_sala_mock_response_correcto():
    """Test corregido: Mock devuelve un objeto (Mock o Sala)."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    service.repository.obtener_por_nombre.return_value = None
    
    # ✅ Mock devuelve un objeto con atributo nombre
    sala_mock = Mock()
    sala_mock.nombre = "Aula A-101"
    sala_mock.id = 1
    
    service.repository.crear.return_value = sala_mock

    sala_data = SalaCreate(
        nombre="Aula A-101",
        piso=1,
        capacidad=30,
        tipo_sala="Aula"
    )

    resultado = service.crear_sala(sala_data)
    
    assert resultado.nombre == "Aula A-101"
    assert resultado.id == 1


# ✅ FALLO 2 - CORREGIDO: Aserción con tipo correcto
def test_obtener_paginacion_skip_limit_correcto():
    """Test corregido: Aserción compara int con int."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    service.repository.filtrar.return_value = [Mock(), Mock(), Mock()]
    service.repository.contar_total.return_value = 10

    resultado = service.obtener_todas_salas(skip=5, limit=3)

    # ✅ Comparar int con int
    assert resultado["skip"] == 5
    assert resultado["limit"] == 3


# ✅ FALLO 3 - CORREGIDO: Validación de limit=0
def test_validar_paginacion_rechaza_limit_cero():
    """Test que valida rechazo de limit=0."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()

    # ✅ Espera HTTPException cuando limit=0
    with pytest.raises(HTTPException) as exc_info:
        service.obtener_todas_salas(skip=0, limit=0)
    
    assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    assert "limit" in exc_info.value.detail


# ✅ FALLO 4 - CORREGIDO: Estructura de respuesta correcta
def test_obtener_salas_estructura_respuesta_correcta():
    """Test corregido: Valida la estructura real de la respuesta."""
    db = Mock()
    service = SalaService(db)
    service.repository = Mock()
    
    sala_mock = Mock()
    sala_mock.id = 1
    sala_mock.nombre = "Aula A-101"
    
    service.repository.filtrar.return_value = [sala_mock]
    service.repository.contar_total.return_value = 1

    resultado = service.obtener_todas_salas()

    # ✅ Validar estructura correcta
    assert "salas" in resultado  # No "resultado"
    assert len(resultado["salas"]) == 1
    assert "total" in resultado
    assert "skip" in resultado
    assert "limit" in resultado
```

### Corrección de código fuente (si aplica)

```python
# app/services/sala_service.py (VERIFICACIÓN)

def _validar_parametros_paginacion(self, skip: int, limit: int) -> None:
    """Valida reglas de paginación."""
    if skip < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="skip no puede ser negativo",
        )
    # ✅ VALIDACIÓN: limit debe ser > 0, no >= 0
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="limit debe estar entre 1 y 100",
        )
```

---

# Rúbrica de evaluación

| Criterio | Excelente (5) | Adecuado (3) | Insuficiente (1) |
|---|---|---|---|
| **Diagnóstico de causa raíz** | Identifica correctamente y justifica con precisión el origen del fallo; distingue entre test, mock y código | Identifica el origen, pero con justificación incompleta | Confunde test, código o entorno; no distingue los tipos |
| **Categorización correcta** | Clasifica 4/4 fallos correctamente (mock, aserción, código, estructura) | Clasifica 2-3 fallos correctamente | Menos de 2 fallos categorizados correctamente |
| **Corrección aplicada** | Minimal, correcta y alineada con contrato funcional; no introduce regresiones | Corrige el fallo pero con cambios innecesarios | No corrige el fallo o introduce nuevos problemas |
| **Validación posterior** | Reejecuta todos los tests y verifica ausencia de regresiones | Reejecuta tests pero no verifica completamente | No verifica la corrección |
| **Reflexión técnica** | Explica diferencia entre mock, aserción y bug; propone mejoras de testabilidad | Explica parcialmente; reflexión superficial | No diferencia tipos de error |
| **Documentación** | Proporciona tabla clasificatoria clara; explicación detallada de cada corrección | Documentación básica pero incompleta | Documentación insuficiente o confusa |

---

## Cierre conceptual

La lección central es que en un entorno de **ALM generativo**, el valor de la IA no está solo en "escribir código", sino en cerrar el ciclo de calidad:

1. **generar** implementación y tests,
2. **ejecutar** validaciones,
3. **diagnosticar** fallos (diferenciando su origen),
4. **reparar** automáticamente,
5. **iterar** hasta estabilidad.

Ese patrón convierte a la IA en un colaborador activo de calidad. El desarrollador, por su parte, aprende a supervisar, validar y guiar ese bucle con criterio técnico y conocimiento del dominio.

---

## Próximos pasos recomendados

1. **Ejercicio práctico**: Ejecutar los tests fallidos en el repositorio y aplicar los prompts con una IA.
2. **Extensión**: Proponer nuevos casos de error y pedir a los alumnos que redacten sus propios prompts de diagnóstico.
3. **Integración CI/CD**: Crear una acción de GitHub que ejecute tests y genere reportes de fallos categorizados.
4. **Evaluación práctica**: Lote de tests reales fallidos para que el alumnado diagnostique y corrija en tiempo limitado.
