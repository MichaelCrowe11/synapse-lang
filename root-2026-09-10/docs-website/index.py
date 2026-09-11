# Vercel WSGI entry point for Synapse Lang
from app_v2 import app

# Vercel looks for 'app' or 'application'
application = app

# For local testing
if __name__ == "__main__":
    app.run()
