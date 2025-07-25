# routes.py

from flask import render_template, redirect, flash, url_for, session, request
from authlib.integrations.base_client.errors import MismatchingStateError
from auth import oauth
import boto3
import uuid
import os

def register_routes(app):

    # Ensure your Flask app has a secret key set for session management
    # app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your-default-secret-key')

    @app.errorhandler(MismatchingStateError)
    def handle_csrf_error(e):
        flash("Session expired. Please try logging in again.")
        return redirect(url_for("index"))

    @app.route('/')
    def index():
        user = session.get('user')
        print("User:", user)
        if user:
            return render_template("chat.html", user=user)
        return render_template("landing.html")

    @app.route('/login')
    def login():
        # Use the callback URL directly as recommended by AWS
        callback_url = 'https://smartsearch.app.ocyonbio.com/authorize'
        print("Redirect URI being used:", callback_url)
        return oauth.oidc.authorize_redirect(callback_url)

    @app.route('/authorize')
    def authorize():
        token = oauth.oidc.authorize_access_token()
        user = token.get('userinfo') or token
        session['user'] = user
        print("User in authorize:", user)
        return redirect(url_for('index'))

    @app.route('/auth/callback')
    def auth_callback():
        # For compatibility, redirect to /authorize
        return redirect(url_for('authorize'))

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        print(f"User logged out: {session.get('user')}")
        return redirect(url_for('index'))

    @app.route("/ask", methods=["POST"])
    def ask_bedrock():
        user = session.get("user")
        if not user:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return {"error": "You must be logged in to ask questions."}, 401
            return render_template("chat.html", user=None, response="You must be logged in to ask questions.")
        if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
            data = request.get_json() or {}
            question = data.get("question", "")
        else:
            question = request.form.get("question", "")
        if not question:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return {"error": "No input provided"}, 400
            return render_template("chat.html", user=user, response="No input provided")
        client = boto3.client(
            "bedrock-agent-runtime",
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        try:
            response_stream = client.invoke_agent(
                agentId=os.getenv("AGENT_ID"),
                agentAliasId=os.getenv("AGENT_ALIAS_ID"),
                sessionId=str(uuid.uuid4()),
                inputText=question
            )
            reply_chunks = []
            for event in response_stream["completion"]:
                if "chunk" in event and "bytes" in event["chunk"]:
                    reply_chunks.append(event["chunk"]["bytes"].decode("utf-8"))
            reply = "".join(reply_chunks)
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return {"reply": reply}
            return render_template("chat.html", user=user, response=reply, question=question)
        except Exception as e:
            if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
                return {"error": str(e)}, 500
            return render_template("chat.html", user=user, response=f"Error: {str(e)}", question=question)
