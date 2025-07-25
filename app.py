from flask import Flask
from auth import configure_oauth
from routes import register_routes
import os
from dotenv import load_dotenv
import sys

load_dotenv()

app = Flask(__name__)

# Set secret key for session security
secret_key = os.getenv("FLASK_SECRET_KEY")
if not secret_key:
    print("WARNING: FLASK_SECRET_KEY is not set! Using an insecure default key. Set FLASK_SECRET_KEY in your environment for production.", file=sys.stderr)
    secret_key = "dev_secret_key"  # fallback for local/dev only
app.secret_key = secret_key

# Secure session cookies (cookie-based sessions only)
app.config.update(
    SESSION_COOKIE_NAME="auth_session",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",  # Must be "Lax" for cross-site redirect
    SESSION_COOKIE_SECURE=os.getenv("DEPLOYED", "false").lower() == "true",  # True in production
)

# Only set SERVER_NAME in deployed environment
if os.getenv("DEPLOYED", "false").lower() == "true":
    # app.config["SERVER_NAME"] = "https://b9u5c3kvef.us-east-1.awsapprunner.com"
    app.config["SERVER_NAME"] = "smartsearch.app.ocyonbio.com"

configure_oauth(app)
register_routes(app)

# Use PORT env variable for App Runner compatibility
if __name__ == "__main__":
    # App Runner sets the PORT env variable; default to 8501 for local dev
    port = int(os.environ.get("PORT", 8501))
    app.run(host="0.0.0.0", port=port)
