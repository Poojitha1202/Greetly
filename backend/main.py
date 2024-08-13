from flask import Flask, jsonify

from Login import auth_blueprint
from SignupPage import registration_blueprint
from CardletCreation import cardlet_creation_app


app = Flask(__name__)

# Register login handler app
app.register_blueprint(auth_blueprint)

# Register registration handler app
app.register_blueprint(registration_blueprint)


# Register capsule creation handler app
app.register_blueprint(cardlet_creation_app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=7000)