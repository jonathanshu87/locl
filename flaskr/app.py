from flask import Flask, request, render_template
import requests
import os
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
    return render_template('home.html')

# create a user
@app.route("/create", methods=['GET', 'POST'])
def create_user(name=None, email=None):
    if request.method == 'GET': 
        # TODO: make a form asking for name and ebt and email
        # TODO: might be easier not to include ebt in this step and have them fill it in on their own in /redeem
        return render_template('create_user.html') # UPDATE THIS TO THE CORRESPONDING HTML FILE!!!!!!!
    elif request.method == 'POST':
        if not name or not email: return "Go lol yourself"

        # create a user in Checkbook
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "86a538fb6584799a755f1a2ab03f6d4b:ce2b54a8e93802433632c4c2ac7f4c54"
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
        new_user = {"id": f'{res["key"]}:{res["secret"]}', "name": name, "balance": 0}
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
    if not user: return "Log in bitch" #UPDATE THIS

    # get the database element for the logged in user
    u = supabase.table('Users').select("*").eq("id", user).execute()
    assert(len(u) == 1)
    data = json.loads(u.data[0])

    # TODO: embed You.com into this 
    return f"""<h1>{data["name"]} has a balance of {data["balance"]}</>"""

# buy a product
@app.route("/buy/<user>/<product>", methods=['POST'])
def buy(user=None, product=None):
    if not user or not product: return "Log in and pick an item bitch"

    # Get product information
    buy_product = supabase.table('Products').select("*").eq("id", product).execute()
    assert(len(buy_product) == 1)
    prod_info = json.loads(buy_product.data[0])

    # Get current user balance
    buy_product = supabase.table('Users').select("*").eq("id", user).execute()
    assert(len(buy_product) == 1)
    user_info = json.loads(buy_product.data[0])

    # update balance
    if user_info["balance"] >= prod_info["price"]:
        _ = supabase.table("Users").update({"balance": int(user_info["balance"]) - int(prod_info["price"])}).eq("id", user).execute()
    else: 
        # TODO: also redirect to marketplace page
        return """Insufficient funds"""

# buy a product
# card info is for ebt
@app.route("/redeem/<user>/", methods=['GET', 'POST'])
def redeem(card_number, expiration_date, cvv, user=None, deposit=0):
    if request.method == 'GET':
        # TODO: have form where people can enter in their ebt and redeem credits
        return """Fuck me"""
    elif request.method == 'POST':
        if not user: return """Log in bitch"""

        # TODO: actually get the money from ebt to us

        # Get current user balance
        buy_product = supabase.table('Users').select("*").eq("id", user).execute()
        assert(len(buy_product) == 1)
        user_info = json.loads(buy_product.data[0])

        # update balance
        _ = supabase.table("Users").update({"balance": int(user_info["balance"]) + int(deposit)}).eq("id", user).execute()
    else:
        return "404: Page not found"