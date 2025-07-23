# routes.py

from flask import render_template, redirect, flash, url_for, session, request
from authlib.integrations.base_client.errors import MismatchingStateError
from auth import oauth
import boto3
import uuid
import os

def register_routes(app):

    @app.errorhandler(MismatchingStateError)
    def handle_csrf_error(e):
        flash("Session expired. Please try logging in again.")
        return redirect(url_for("home"))  # or login

    @app.route('/')
    def index():
        user = session.get('user')
        if user:
            # return  f'Hello, {user["email"]}. <a href="/logout">Logout</a>'
            return render_template("index.html", user=user)
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        # Alternate option to redirect to /authorize
        redirect_uri = url_for('authorize', _external=True, _scheme='https') 
        return oauth.oidc.authorize_redirect(redirect_uri)
        # return oauth.oidc.authorize_redirect('http://localhost:8501/authorize')

    @app.route('/authorize')
    def authorize():
        try:
            token = oauth.oidc.authorize_access_token()
            user = token['userinfo']
            session['user'] = user
            return redirect(url_for('index'))
        except Exception as e:
            return f"Authorization error: {str(e)}", 500

    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect(url_for('index'))

    @app.route("/ask", methods=["POST"])
    def ask_bedrock():
        user = session.get("user")
        if not user:
            return redirect(url_for("login"))

        question = request.form.get("question", "")
        if not question:
            return "No input provided", 400

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
            return render_template("index.html", user=user, response=reply, question=question)

        except Exception as e:
            return render_template("index.html", user=user, response=f"Error: {str(e)}", question=question)
