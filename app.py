from flask import Flask, render_template, request
from obfuscate import obfuscate_bp
from werkzeug.middleware.proxy_fix import ProxyFix

def create_app():
    
    import os
    
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "fallback-key")

    # Apply ProxyFix to ensure Flask handles headers from Nginx correctly
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

    # app.config['SESSION_COOKIE_DOMAIN'] = 'www.obfusquate.com'

    # Register blueprints
    app.register_blueprint(obfuscate_bp)

    # Define index route
    @app.route('/')
    def home():
        return render_template('index.html', current_path=request.path)

    @app.route('/methods')
    def methods():
        return render_template('methods.html', current_path=request.path)

    @app.route('/quantumEncryption')
    def quantum_encryption():
        return render_template('quantum_encryption.html', current_path=request.path)
    
    @app.route('/aboutUs')
    def about_us():
        return render_template('about_us.html', current_path=request.path)

    @app.route('/howTo')
    def how_to():
        return render_template('how_to.html', current_path=request.path)

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(500)
    @app.errorhandler(502)
    @app.errorhandler(503)
    @app.errorhandler(504)
    def handle_error(e):
        return render_template('error.html'), e.code if hasattr(e, 'code') else 500

    return app

# Create the Flask application instance
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
