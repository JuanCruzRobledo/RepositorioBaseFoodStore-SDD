# 08 — Arquitectura Propuesta

---

## Backend — Arquitectura en Capas

### Principio Rector

```
Router → Service → UoW → Repository → Model
```

**Ninguna capa puede importar de la capa superior.** El flujo de dependencias es estrictamente unidireccional.

### Patrón Unit of Work (UoW)

El UoW es el director de orquesta que garantiza atomicidad transaccional. Se implementa como **context manager** de Python:

```python
class UnitOfWork:
    def __aenter__(self):
        self.session = SessionFactory()
        self.productos = ProductoRepository(self.session)
        self.pedidos = PedidoRepository(self.session)
        self.detalles = DetallePedidoRepository(self.session)
        self.historial = HistorialRepository(self.session)
        # ... otros repositorios
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()
        await self.session.close()
```

**Uso en Service:**
```python
async def crear_pedido(uow: UnitOfWork, body: CrearPedidoRequest, usuario_id: int):
    async with uow:
        # Toda la lógica aquí
        # Si se lanza excepción → rollback automático
        # Si termina sin excepción → commit automático
```

**Regla:** Los Services **nunca** llaman `session.commit()` directamente.

### BaseRepository[T] Genérico

```python
class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: Type[T]):
        self.session = session
        self.model = model

    async def get_by_id(self, id: int) -> T | None:
        # Excluye soft-deleted por defecto

    async def list_all(self, skip: int, limit: int) -> list[T]:
        # Excluye soft-deleted por defecto

    async def count(self) -> int: ...

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()   # obtiene ID sin commit
        await self.session.refresh(entity)
        return entity

    async def update(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def soft_delete(self, entity: T) -> None:
        entity.eliminado_en = datetime.utcnow()
        await self.session.flush()

    async def hard_delete(self, entity: T) -> None:
        await self.session.delete(entity)
        await self.session.flush()
```

**Repositorios especializados** heredan de `BaseRepository[T]` y agregan queries de dominio:

```python
class ProductoRepository(BaseRepository[Producto]):
    async def buscar_por_categoria(self, categoria_id: int) -> list[Producto]: ...
    async def actualizar_stock(self, producto_id: int, delta: int) -> None: ...

class PedidoRepository(BaseRepository[Pedido]):
    async def listar_por_usuario(self, usuario_id: int) -> list[Pedido]: ...
    async def listar_por_estado(self, estado_codigo: str) -> list[Pedido]: ...
```

---

## Backend — Organización de Módulos (Feature-First)

```
app/
├── core/
│   ├── config.py          # Variables de entorno (pydantic-settings)
│   ├── database.py        # Engine y AsyncSession factory
│   ├── security.py        # Hash bcrypt, JWT encode/decode
│   └── uow.py             # UnitOfWork
├── modules/
│   ├── auth/
│   │   ├── model.py       # RefreshToken model
│   │   ├── schemas.py     # LoginRequest, RegisterRequest, TokenResponse
│   │   ├── repository.py  # RefreshTokenRepository
│   │   ├── service.py     # login(), register(), refresh(), logout()
│   │   └── router.py      # POST /auth/login, /register, /refresh, /logout
│   ├── usuarios/
│   │   └── ...            # (misma estructura)
│   ├── categorias/
│   ├── productos/
│   ├── pedidos/
│   ├── pagos/
│   └── admin/
├── db/
│   └── seed.py            # Script de datos iniciales
├── dependencies.py        # get_current_user(), require_role()
└── main.py               # FastAPI app, CORS, rate limiting, routers
```

---

## Frontend — Feature-Sliced Design (FSD)

### Estructura de Directorios

```
src/
├── app/
│   ├── providers.tsx      # QueryClientProvider, RouterProvider
│   ├── router.tsx         # Definición de rutas
│   └── styles/
├── pages/
│   ├── CatalogoPage.tsx
│   ├── CheckoutPage.tsx
│   ├── MisPedidosPage.tsx
│   └── admin/
│       ├── DashboardPage.tsx
│       └── PedidosAdminPage.tsx
├── features/
│   ├── auth/              # LoginForm, RegisterForm, ProtectedRoute HOC
│   ├── store/             # CatalogoGrid, CartDrawer, CheckoutForm, CardPayment
│   ├── pedidos/           # PedidosList, PedidoDetail, HistorialTimeline
│   └── admin/             # Dashboard KPIs, CRUDs, GestionPedidos, StockTable
├── hooks/                 # Custom hooks con TanStack Query
│   ├── useAuth.ts         # useLogin, useRegister, useMe
│   ├── useProductos.ts    # useProductos, useProducto
│   ├── usePedidos.ts      # usePedidos, usePedido, useAvanzarEstado
│   └── usePagos.ts        # useCrearPago, usePagoStatus
├── shared/
│   ├── stores/
│   │   ├── authStore.ts   # access/refresh token, usuario, isAuthenticated
│   │   ├── cartStore.ts   # items, addItem, removeItem, clearCart
│   │   ├── paymentStore.ts # status de pago, mpPaymentId
│   │   └── uiStore.ts     # cartOpen, sidebarOpen, modals
│   ├── api/
│   │   └── axios.ts       # Instancia + interceptores Bearer + refresh 401
│   └── components/        # Button, Input, Badge, Modal, Skeleton, Toast
└── types/
    └── index.ts           # Producto, Pedido, Usuario, Pago, CartItem, etc.
```

### Los Cuatro Stores de Zustand

| Store | Persiste | Estado |
|-------|----------|--------|
| `authStore` | ✅ Solo `accessToken` | `accessToken`, `usuario`, `isAuthenticated` |
| `cartStore` | ✅ Items completos | `items[]`, `totalItems()`, `totalPrice()` |
| `paymentStore` | ❌ Solo sesión | `status`, `mpPaymentId`, `error` |
| `uiStore` | ❌ Efímero | `cartOpen`, `sidebarOpen`, modals |

**Buenas prácticas:**
```typescript
// ✅ Suscripción por slice (evita re-renders innecesarios)
const itemCount = useCartStore(s => s.items.length)

// ✅ Acceso fuera de React (interceptores Axios)
const token = useAuthStore.getState().accessToken

// ❌ Nunca suscribirse al store completo
const store = useCartStore() // INCORRECTO
```

---

## Patrones de Diseño Aplicados

| Patrón | Capa | Descripción |
|--------|------|-------------|
| **Repository Pattern** | Backend | Abstracción del acceso a BD. `BaseRepository[T]` genérico. Facilita testing con mocks. |
| **Unit of Work** | Backend | Gestión de transacciones atómicas. El Service opera dentro del contexto UoW sin gestionar la sesión directamente. |
| **Service Layer** | Backend | Lógica de negocio centralizada, stateless. Consume el UoW. Independiente del framework HTTP. |
| **Snapshot Pattern** | Backend/BD | Precios y nombres de producto inmutables al crear el pedido. Garantiza integridad histórica. |
| **Soft Delete** | Backend/BD | `eliminado_en` TIMESTAMPTZ — registros lógicamente eliminados. Nunca DELETE físico en entidades de negocio. |
| **Audit Trail Append-Only** | Backend/BD | `HistorialEstadoPedido`: solo INSERT, nunca UPDATE/DELETE. Trazabilidad completa. |
| **State Machine (FSM)** | Backend | Transiciones del pedido validadas en la capa de Service contra el mapa de transiciones permitidas. |
| **Idempotent Payments** | Backend | UUID como `idempotency_key` enviado a MercadoPago. Evita cobros duplicados por reintentos. |
| **Feature-Sliced Design** | Frontend | Organización por features con límites de importación claros. Cada feature es autocontenida. |
| **Custom Hooks** | Frontend | Encapsulan lógica de TanStack Query en hooks reutilizables por dominio. |
| **Optimistic Updates** | Frontend | Actualización inmediata de UI antes de confirmar respuesta del servidor. Rollback en error. |
| **Webhook / IPN** | Backend | MercadoPago notifica de forma asíncrona el resultado del pago. Evita polling constante. |

---

## Seguridad

### Autenticación JWT (doble token)

```
Access Token:  30 minutos | Payload: userId + email + roles | HS256
Refresh Token: 7 días     | UUID v4 opaco | Almacenado en BD | Rotación en cada uso
```

### PCI DSS SAQ-A

Los datos de tarjeta **nunca** pasan por los servidores de Food Store. La tokenización ocurre en el browser mediante `MercadoPago.js` / `@mercadopago/sdk-react`. Solo el `card_token` (opaco) viaja al backend.

### Rate Limiting

```python
# slowapi — aplicado en main.py + decorador en router de auth
@limiter.limit("5/15minutes")
@router.post("/auth/login")
async def login(request: Request, body: LoginRequest):
    ...
```

### CORS

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,  # ["http://localhost:5173"] en dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Variables de Entorno Requeridas

### Backend (`.env`)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `DATABASE_URL` | Conexión PostgreSQL | `postgresql+asyncpg://user:pass@localhost:5432/foodstore` |
| `SECRET_KEY` | Clave secreta JWT (min 32 chars) | `your-super-secret-key...` |
| `ALGORITHM` | Algoritmo JWT | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Duración access token | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Duración refresh token | `7` |
| `CORS_ORIGINS` | Orígenes permitidos (JSON) | `["http://localhost:5173"]` |
| `MP_ACCESS_TOKEN` | Access Token MercadoPago | `TEST-xxxx` |
| `MP_PUBLIC_KEY` | Public Key MercadoPago | `TEST-xxxx` |
| `MP_NOTIFICATION_URL` | URL del webhook IPN | `https://dominio.com/api/v1/pagos/webhook` |

### Frontend (`.env`)

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `VITE_API_URL` | URL base del backend | `http://localhost:8000` |
| `VITE_MP_PUBLIC_KEY` | Public Key MP (frontend) | `TEST-xxxx` |

---

## Checklist de Entrega

| Ítem | Descripción |
|------|-------------|
| CE-01 | Link a repositorio GitHub público |
| CE-02 | README.md con instrucciones de setup |
| CE-03 | `.env.example` completo con variables MP documentadas |
| CE-04 | `alembic upgrade head` sin errores |
| CE-05 | `python -m app.db.seed` carga datos iniciales |
| CE-06 | `npm install + npm run dev` sin errores |
| CE-07 | `pip install -r requirements.txt + uvicorn app.main:app` sin errores |
| CE-08 | Swagger UI (`/docs`) con todos los endpoints documentados |
| CE-09 | Pago de prueba con tarjeta sandbox MP funciona end-to-end |
| CE-10 | Unit of Work correctamente implementado (ningún `session.commit()` directo en services) |
| CE-11 | 4 Zustand stores implementados, tipados y con `persist` correcto |
| CE-12 | Screenshots de al menos 10 pantallas distintas |
| CE-13 | Link a video demostración (5-10 min) en README |
| CE-14 | Repositorio público verificado con sesión cerrada |

**Penalización:** -30% si el proyecto no corre localmente siguiendo el README.

**Bonus:** +10pts tests unitarios (pytest, cobertura > 60%) | +10pts deploy funcional

---

## Referencias Cruzadas

- → [04_modelo_de_datos.md](04_modelo_de_datos.md) — Entidades del modelo
- → [07_flujos_principales.md](07_flujos_principales.md) — Flujo UoW en creación de pedido
- → [02_descripcion_general.md](02_descripcion_general.md) — Stack tecnológico
