from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from flask_mail import Mail, Message

app = Flask(__name__, static_folder="assets", template_folder=".")

# Flask-Mail Configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_USERNAME")

mail = Mail(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/images/<path:filename>")
def serve_images(filename):
    return send_from_directory("images", filename)


@app.route("/favicon.png")
def favicon():
    return send_from_directory(".", "favicon.png")


@app.route("/contact", methods=["POST"])
def contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message_body = data.get("message")

    if not all([name, email, message_body]):
        return jsonify({"status": "error", "message": "Missing fields"}), 400

    try:
        msg = Message(
            subject=f"Portfolio Contact: {name}",
            recipients=["ahnafzakaria88@gmail.com"],
            body=f"Name: {name}\nEmail: {email}\n\nMessage:\n{message_body}",
        )
        mail.send(msg)
        print(f"Email sent from {email}")
        return jsonify(
            {
                "status": "success",
                "message": "Message sent successfully. I will get back to you soon.",
            }
        ), 200
    except Exception as e:
        print(f"Failed to send email: {e}")
        return jsonify(
            {
                "status": "error",
                "message": "Failed to send message. Please try again later.",
            }
        ), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
