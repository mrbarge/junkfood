from junkfood import create_app

try:
    # Werkzeug 0.15 and newer
    from werkzeug.middleware.proxy_fix import ProxyFix
except ImportError:
    # older releases
    from werkzeug.contrib.fixers import ProxyFix

if __name__ == "__main__":
    app = create_app()
    app.debug = True
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run(host='0.0.0.0', port=8080)
