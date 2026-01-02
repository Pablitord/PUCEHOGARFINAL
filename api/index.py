from app import create_app

# Vercel buscará la variable 'app' como callable WSGI
app = create_app()

