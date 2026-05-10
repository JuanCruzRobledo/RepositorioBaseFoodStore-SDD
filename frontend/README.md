# Frontend — Food Store

React + TypeScript + Vite, Feature-Sliced Design.

## Setup

```bash
cd frontend
npm install
cp .env.example .env                # completar VITE_API_URL=http://localhost:8000
npm run dev
```

App en `http://localhost:5173`.

## Estructura (Feature-Sliced Design)

```
frontend/src/
├── app/               composicion raiz, routing, providers, ErrorBoundary
├── features/          features funcionales (un subdir por feature)
├── entities/          modelos de dominio reutilizables
└── shared/
    ├── api/           cliente HTTP + interceptor global
    └── stores/        4 stores Zustand persistidos en localStorage
        ├── authStore.ts
        ├── cartStore.ts
        ├── uiStore.ts
        └── userStore.ts
```

## Convenciones

- Estado servidor: `@tanstack/react-query`.
- Estado cliente: Zustand con `persist` (clave prefijada `foodstore.<store>`).
- Forms: `@tanstack/react-form`.
- Componentes: `PascalCase.tsx`. Utilidades: `kebab-case.ts`.
- Capas inferiores no importan de capas superiores (FSD enforcement).

## Build

```bash
npm run build
```
