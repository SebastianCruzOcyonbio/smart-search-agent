from flask import Flask
from auth import configure_oauth
from routes import register_routes
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# Secure session cookies (cookie-based sessions only)
app.config.update(
    SESSION_COOKIE_NAME="auth_session",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",  # Must be "Lax" for cross-site redirect
    SESSION_COOKIE_SECURE=os.getenv("DEPLOYED", "false").lower() == "true",  # True in production
)

# Only set SERVER_NAME in deployed environment
if os.getenv("DEPLOYED", "false").lower() == "true":
    app.config["SERVER_NAME"] = "b9u5c3kvef.us-east-1.awsapprunner.com"

configure_oauth(app)
register_routes(app)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8501)
