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

### Desarrollo Local
**Desde el directorio raíz del proyecto:**
```bash
python src/main.py
```

### Producción (con Gunicorn)
```bash
gunicorn --bind 0.0.0.0:5000 src.main:app
```

### Para deployment en plataformas como Render:
**Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`

El servidor se ejecutará en `http://localhost:5000` (desarrollo) o en el puerto especificado (producción)

## 🚀 Deployment en Render.com

### Configuración Rápida
1. **Build Command**: `pip install -r requirements.txt`
2. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT src.main:app`
3. **Health Check Path**: `/api/sandbox/health`

### Variables de Entorno Requeridas
```bash
FLASK_ENV=production
SECRET_KEY=tu_clave_secreta_muy_larga
CORS_ORIGINS=https://tu-frontend-url.onrender.com
```

### Variables Opcionales
```bash
OPENAI_API_KEY=tu_api_key_para_funciones_ia
DATABASE_URL=sqlite:///./database/app.db
REDIS_URL=redis://localhost:6379/0
```

📖 **Ver guía completa en**: `RENDER_DEPLOYMENT_GUIDE.md`

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
