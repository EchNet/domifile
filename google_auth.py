from flask_dance.contrib.google import make_google_blueprint, google

#
# Users login and access the services having authenticated with OAuth.
# We don't store OAuth credentials.  Therefore, automation must authenticate
# using a service account.
#
# Thinking about personal edition... The service account could be owned by
# the app and granted the permission by the user.  Like the Staples experience.
#


def define_google_auth(app):
  """ Google OAuth Setup """
  GOOGLE_CLIENT_ID = app.config["GOOGLE_CLIENT_ID"]
  GOOGLE_CLIENT_SECRET = app.config["GOOGLE_CLIENT_SECRET"]

  google_bp = make_google_blueprint(client_id=GOOGLE_CLIENT_ID,
                                    client_secret=GOOGLE_CLIENT_SECRET,
                                    scope=[
                                        "openid",
                                        "https://www.googleapis.com/auth/drive.metadata.readonly",
                                        "https://www.googleapis.com/auth/userinfo.email"
                                    ],
                                    redirect_to="admin_screen")
  app.register_blueprint(google_bp, url_prefix="/login")
