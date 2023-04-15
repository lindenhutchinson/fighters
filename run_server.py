#!/usr/bin/python
from app import create_app, register_extensions
from config import DevelopmentConfig, ProductionConfig

# Create an app instance and run
if __name__ == '__main__':
    app = create_app(DevelopmentConfig())
    register_extensions(app)
    port = int(app.config['PORT'])
    host = app.config['HOST']
    app.run(host=host, port=port)
