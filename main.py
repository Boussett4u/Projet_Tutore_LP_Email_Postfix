from flask import Flask, flash, redirect, url_for, render_template
from flask_recaptcha import Recaptcha


app = Flask(__name__)

#Instance de Recaptcha
recaptcha = Recaptcha(app=app)


# Se rendre sur le site Recaptcha, générer un captcha v2 (je ne suis pas un robot)
# Cliquer sur envoyer, ça va générer 2 clefs (Site et privée)
# Ici on met les clef du site et clef privée relatif au recaptcha

app.config.update(dict(
    RECAPTCHA_ENABLED=True,
    RECAPTCHA_SITE_KEY="6LeHBS0eAAAAAEEjwVT57Zi7RqRgAbOF7TWOOaeF",
    RECAPTCHA_PRIVATE_KEY="6LeHBS0eAAAAAHHitmwv8YSnY5vJVnTbjxMhABJ8"
))

# On initialise le Recaptcha
recaptcha = Recaptcha()
recaptcha.init_app(app)

# Pas utile ici
# app.config['SECRET_KEY'] = 'cairocoders-ednalan'

# Page 1
# Page racine (défaut)


@app.route("/home")
def home():
    return render_template("test.html")

# Page 2
# Affiche ce qu'il y a après "/"


@app.route("/<name>")
def user(name):
    return f"Hello {name} !"


# Page 3 - Redirection
# Redirige vers une autre page


@app.route("/admin")
def admin():
    return redirect(url_for("user", name="Admin"))

# Page 4 - Submit
# Si recaptcha bon, alors ça fait une action (redirection, etc.)
# Si recaptcha pas bon, alors ça fait rien


@app.route("/submit", methods=["POST"])
def submit():
    if recaptcha.verify():
        flash('You are connected')
        redirect(url_for("name", name="User"))
    else:
        flash('You are not connected')
        return redirect(url_for("home"))


# 2 dernières ligne, pour afficher la page web

if __name__ == '__main__':
    app.run(debug=True)
