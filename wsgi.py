"""
WSGI entry point for production
"""
from web.app import app

if __name__ == "__main__":
    app.run() 