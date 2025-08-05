# Backend - Sistema de IA Assistant

## Instalación

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (opcional para funcionalidades AI):
```bash
export OPENAI_API_KEY=tu_api_key_aqui
```

## Ejecución

**Desde el directorio raíz del proyecto:**
```bash
python src/main.py
```

El servidor se ejecutará en `http://localhost:5000`

## Características

- API REST con Flask
- Asistente de IA integrado
- Soporte para OpenAI GPT
- CORS habilitado para frontend
- Base de datos SQLite
- Rutas modulares

## Endpoints disponibles

- `/api/` - Rutas de usuario
- `/api/ai/` - Asistente de IA
- `/api/repair/` - Reparación automática
- `/api/deploy/` - Despliegue automático

## Notas importantes

- El cliente OpenAI se inicializa solo cuando se necesita
- Si no se configura OPENAI_API_KEY, las funciones de IA no estarán disponibles
- La aplicación sirve archivos estáticos desde la carpeta `src/static`
