from authlib.integrations.flask_client import OAuth
import os

oauth = OAuth()

def configure_oauth(app):
    oauth.init_app(app)

    oauth.register(
        name='oidc',
        client_id=os.getenv("COGNITO_CLIENT_ID", "4ec9umqa6do12563uqijil9261"),
        client_secret=os.getenv("COGNITO_CLIENT_SECRET"),
        server_metadata_url='https://cognito-idp.us-east-1.amazonaws.com/us-east-1_cL4iYcyYg/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )
