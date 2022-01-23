from flask import Flask, flash, redirect, url_for, render_template
from flask_recaptcha import Recaptcha


app = Flask(__name__)
recaptcha = Recaptcha(app=app)

app.config.update(dict(
    RECAPTCHA_ENABLED=True,
    RECAPTCHA_SITE_KEY="6LeHBS0eAAAAAEEjwVT57Zi7RqRgAbOF7TWOOaeF",
    RECAPTCHA_PRIVATE_KEY="6LeHBS0eAAAAAHHitmwv8YSnY5vJVnTbjxMhABJ8"
))
app.config["RECAPTCHA_PUBLIC_KEY"] = "KEY GOES HERE "
app.config["RECAPTCHA_PRIVATE_KEY"] = "PRIVATE KEY GOES HEREE"

recaptcha = Recaptcha()
recaptcha.init_app(app)

app.config['SECRET_KEY'] = 'cairocoders-ednalan'

# Page 1
# Main (default) page


@app.route("/home")
def home():
    return render_template("test.html")

# Page 2
# Print the specified word after "/"


@app.route("/<name>")
def user(name):
    return f"Hello {name} !"


# Page 3 - Redirection
# If admin then it redirects to another page


@app.route("/admin")
def admin():
    return redirect(url_for("user", name="Admin"))

# Page 4 - Submit
# If test passed, then rediction
# If test failed, then nothing


@app.route("/submit", methods=["POST"])
def submit():
    if recaptcha.verify():
        flash('You are connected')
        redirect(url_for("name", name="User"))
    else:
        flash('You are not connected')
        return redirect(url_for("home"))


# Run the web page to see it in the browser

if __name__ == '__main__':
    app.run(debug=True)
