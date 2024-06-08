from flask import Flask
from flask_kerberos import requires_authentication, init_kerberos

app = Flask(__name__)

# Initialize Kerberos
kerberos = init_kerberos(app)


# Route that requires Kerberos authentication
@app.route('/protected')
@requires_authentication
def protected_view(user):
    return f'Hello, {user}'


# Route that doesn't require authentication
@app.route('/')
def public_view():
    return 'This is a public page.'


if __name__ == '__main__':
    app.run(debug=True)
