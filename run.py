import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', '247csa.settings')
django.setup()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "247csa.asgi:application",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 