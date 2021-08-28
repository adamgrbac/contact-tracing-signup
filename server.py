from flask import Flask, render_template, request
import requests
import yaml
import yagmail


with open("config.yml", "r") as f:
    config = yaml.safe_load(f)

yag = yagmail.SMTP(config["sender"], oauth2_file="oauth2_file.json")

def add_to_list(email, state):
    print(f"Adding {email} to {state} list...")
    with open(config["state_dict"][state], "r+") as f:
        email_config = yaml.safe_load(f)
    if email.lower() not in email_config["dist_list"]:
        email_config["dist_list"].append(email.lower())
        with open(config["state_dict"][state], "w+") as tmp:
            yaml.dump(email_config, tmp, default_flow_style=False)
        yag.send(to="adam.grbac@gmail.com", subject="New Covid Mailer User!", contents=f"{email} added to {state} dist list!")
    else:
        print("Already on list!")


def remove_from_list(email, state):
    print(f"Removing {email} from {state} list...")
    with open(config["state_dict"][state], "r+") as f:
        email_config = yaml.safe_load(f)
    if email.lower() in email_config["dist_list"]:
        email_config["dist_list"].remove(email.lower())
        with open(config["state_dict"][state], "w+") as tmp:
            yaml.dump(email_config, tmp, default_flow_style=False)
        yag.send(to="adam.grbac@gmail.com", subject="Unsubscribed Covid Mailer User!", contents=f"{email} removed from {state} dist list!")
    else:
        print("Not in list!")


app = Flask(__name__)

@app.route("/")
def hello_world():
	return render_template("index.html")
    
@app.route("/unsubscribe")
def hello_world():
	return render_template("unsubscribe.html")

@app.route("/unsubscribe/submit", methods=["POST"])
@app.route("/submit", methods=["POST"])
def submit():
    captcha_response = request.form.get('g-recaptcha-response')
    captcha_secret = config["captcha_secret"] 
    res = requests.post(f"https://www.google.com/recaptcha/api/siteverify?secret={captcha_secret}&response={captcha_response}")
    if res.json()["success"]:
        if "unsubscribe" in request.path:
            remove_from_list(request.form.get('email'),request.form.get('state')) 
            return f"<p>{request.form.get('email')} removed from {request.form.get('state')} list!</p>"
        else:
            add_to_list(request.form.get('email'),request.form.get('state')) 
            return f"<p>{request.form.get('email')} added to {request.form.get('state')} list!</p>"
    else:
        return "Captcha challenge failed! Try again."
	
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=1337)
