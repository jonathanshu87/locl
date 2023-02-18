from flask import Flask, request
import requests
import os
# TODO: might be easier just to use REST instead of python API bc it sucks
# https://www.jitsejan.com/creating-quick-app-with-supabase
from supabase import create_client, Client
import json

app = Flask(__name__)

# supa_url: str = os.environ.get("SUPABASE_URL")
# supa_key: str = os.environ.get("SUPABASE_KEY")

supa_url: str = "https://jzjvqqnpxpmrsqwooipn.supabase.co"
supa_key: str = "teyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp6anZxcW5weHBtcnNxd29vaXBuIiwicm9sZSI6ImFub24iLCJpYXQiOjE2NzY3MDUxMzUsImV4cCI6MTk5MjI4MTEzNX0.I1zPmUnmOOXM2opyktaMFU3oji7cHMlEPE8rAin0gI8"
supabase: Client = create_client(supa_url, supa_key)

user_url = "https://sandbox.checkbook.io/v3/user"
vcc_url = "https://sandbox.checkbook.io/v3/account/vcc"

@app.route("/")
def hello():
    # TODO: add a create user button that redirects to /create & a sign in button which doesn't do anything
    return """<h1>Hello, World!</h1>"""

# create a user
@app.route("/create", methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET': 
        # TODO: make a form asking for name and ebt and email
        # TODO: might be easier not to include ebt in this step and have them fill it in on their own in /redeem
        return """<h1>Enter your details</>"""
    elif request.method == 'POST':

        # get the attributes from the post request form
        name = request.args.get('name')
        ebt = request.args.get('ebt')
        email = request.args.get('email')

        # create a user in Checkbook
        # TODO: how do we add Authorization in header, when we only get that as the post request response
        # https://docs.checkbook.io/reference/onboard-user
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f'{res["key"]}:{res["secret"]}'
        }
        user_payload = {
            "user_id": f"{email}",
            "name": f"{name}"
        }
        user_response = requests.post(user_url, json=user_payload, headers=headers)

        # response credentials
        # res["key"]
        # res["secret"]
        # res["user_id"]  
        res = json.loads(user_response.text)

        # make virtual credit card (vcc)
        # TODO: do we just want to hardcode an address in?
        # https://docs.checkbook.io/reference/post-vcc
        vcc_payload = {"address": {
            "line_1": "1234 N. 1st Street",
            "city": "San Francisco",
            "state": "CA",
            "zip": "12345"
        }}
        vcc_response = requests.post(vcc_url, json=vcc_payload, headers=headers)

        # response virtual credit card
        # res["id"]
        # res["card_number"]
        # res["expiration_date"]
        # res["cvv"]
        res = json.loads(vcc_response.text)

        # add user to Users table
        # id = checkbook authorization
        new_user = {"id": f'{res["key"]}:{res["secret"]}', "name": name, "balance": 0, "ebt": ebt}
        _ = supabase.table('Users').insert(new_user).execute()

        # add vcc to user and add it to VCC table
        # user_id = checkbook authorization
        # id = unique card identifier
        new_vcc = {"user_id": f'{res["key"]}:{res["secret"]}', "id": res["id"], "card_number": res["card_number"], "expiration_date": res["expiration_date"], "cvv": res["cvv"]}
        _ = supabase.table('VCC').insert(new_vcc).execute()
    else:
        return "404 Error: Page not found"

# marketplace for logged in user
@app.route("/marketplace/<user>", methods=['GET'])
def marketplace(user=None):
    if not user: return "Log in bitch"

    # get the database element for the logged in user
    u = supabase.table('Users').select("*").eq("id", user).execute()
    data = json.loads(u.data)

    # TODO: embed You.com into this 
    return f"""<h1>{data["name"]} has a balance of {data["balance"]}</>"""

# buy a product
@app.route("/buy/<user>/<product>", methods=['POST'])
def buy(user=None, product=None):
    if not user or not product: return "Log in and pick an item bitch"

    # TODO: update balance based on purchase

# buy a product
@app.route("/redeem/<user>/", methods=['GET', 'POST'])
def redeem(user=None):
    if request.method == 'GET':
        # TODO: have form where people can enter in their ebt and redeem credits
        return """Fuck me"""
    elif request.method == 'POST':
        # TODO: take money from ebt and deposit credits into user's VCC
        pass
    else:
        return "404: Page not found"