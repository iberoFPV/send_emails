from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    url_for,
    redirect,
    current_app,
)
from app.db import get_db

# bred api
import time
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from pprint import pprint
import os

bp = Blueprint("mail", __name__, url_prefix="/")


@bp.route("/", methods=["GET"])
def index():
    search = request.args.get("serch")
    db, c = get_db()

    if search is None:
        c.execute("SELECT * FROM email")
    else:
        c.execute("SELECT * from email WHERE content LIKE %s", ("%" + search + "%",))
    mails = c.fetchall()

    return render_template("mails/index.html", mails=mails)


@bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        email = request.form.get("email")
        subject = request.form.get("subject")
        content = request.form.get("content")
        errors = []

        if not email:
            errors.append("Email es obligatorio")

        if not subject:
            errors.append("Asunto es obligatorio")

        if not content:
            errors.append("Contenido es obligatorio")

        if len(errors) == 0:
            send_email(email, subject, content)
            db, c = get_db()
            c.execute(
                "INSERT INTO email (email, subject, content) VALUES (%s, %s, %s)",
                (email, subject, content),
            )
            db.commit()

            return redirect(url_for("mail.index"))
        else:
            for error in errors:
                flash(error)
    return render_template("mails/create.html")


def send_email(to, subject, content):
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = os.environ["SENDGRID_KEY"]
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    subject = subject
    sender = {"email": "tu_email@proton.me"}
    to = [{"email": to}]
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=to, text_content=content, sender=sender, subject=subject
    )
    try:
        # Send a transactional email
        api_response = api_instance.send_transac_email(send_smtp_email)
        pprint(api_response)
    except ApiException as e:
        print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
