from flask import Flask, request, render_template, redirect
import requests
import os
from supabase import create_client, Client
import json

app = Flask(__name__)

# supa_url: str = os.environ.get("SUPABASE_URL")
# supa_key: str = os.environ.get("SUPABASE_KEY")

supa_url: str = "https://jzjvqqnpxpmrsqwooipn.supabase.co"
supa_key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imp6anZxcW5weHBtcnNxd29vaXBuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY3NjcwNTEzNSwiZXhwIjoxOTkyMjgxMTM1fQ.6lsTCYOKvVqgcqiDrH7K4PLsxU6kPxss3hPyB7JA5zM"
supabase: Client = create_client(supa_url, supa_key)

user_url = "https://sandbox.checkbook.io/v3/user"
vcc_url = "https://sandbox.checkbook.io/v3/account/vcc"


@app.route("/")
def hello():
    return render_template('home.html')

# create a user
@app.route("/create", methods=['GET', 'POST'])
def create_user():
    if request.method == 'GET': 
        return render_template('create_user.html') 
    elif request.method == 'POST':
        if not request.form["name"] or not request.form["email"]: return render_template('error.html')

        name = request.form["name"]
        email = request.form["email"]

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
        user_res = json.loads(user_response.text)

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
        vcc_res = json.loads(vcc_response.text)

        # add user to Users table
        # id = checkbook authorization
        new_user = {"id": f'{user_res["key"]}:{user_res["secret"]}', "name": name, "balance": 0, "email": email}
        _ = supabase.table('Users').insert(new_user).execute()

        # add vcc to user and add it to VCC table
        # user_id = checkbook authorization
        # id = unique card identifier
        new_vcc = {"user_id": f'{user_res["key"]}:{user_res["secret"]}', "id": vcc_res["id"], \
                    "card_number": vcc_res["card_number"], "expiration_date": vcc_res["expiration_date"], "cvv": vcc_res["cvv"]}
        _ = supabase.table('VCC').insert(new_vcc).execute()

        return redirect(f'/marketplace/{user_res["key"]}%3A{user_res["secret"]}')
    else:
        return "404 Error: Page not found"

# marketplace for logged in user
@app.route("/marketplace/<user>", methods=['GET'])
def marketplace(user=None):
    # get the database element for the logged in user
    u = supabase.table('Users').select("*").eq("id", user).execute()
    data = u.data[0]
    
    p = supabase.table("Products").select("*").execute()
    products = p.data

    s = supabase.table("Store").select("*").execute()
    store = s.data

    full_list = []
    for i in products:
        for j in store:
            if i["store"] == j["id"]: 
                full_list.append({
                    "name": j["name"],
                    "item": i["product"],
                    "price": i["price"],
                    "id": i["id"]
                })

    return render_template('marketplace.html', id=user, name=data["name"], balance=data["balance"], products=full_list)

# buy a product
@app.route("/buy/<user>/<product>", methods=['GET'])
def buy(user=None, product=None):
    if not user or not product: return render_template('error.html')

    # Get product information
    buy_product = supabase.table('Products').select("*").eq("id", product).execute()
    prod_info = buy_product.data[0]

    # Get current user balance
    users = supabase.table('Users').select("*").eq("id", user).execute()
    user_info = users.data[0]

    # update balance
    if user_info["balance"] >= prod_info["price"]:

        _ = supabase.table("Users").update({"balance": int(user_info["balance"]) - int(prod_info["price"])}).eq("id", user).execute()

        return redirect(f'/marketplace/{user}')
    else: 
        return render_template('marketplace.html', error="Insufficent Funds")

# buy a product
# card info is for ebt
@app.route("/redeem/<user>", methods=['GET', 'POST'])
def redeem(user=None):
    if request.method == 'GET':
        return render_template("redeem.html", user=user)
    elif request.method == 'POST':
        if not request.form["card_number"] or not request.form["expiration_date"] or not request.form["cvv"] or \
            not request.form["deposit"] or not user: 
            return render_template("error.html")
        # return render_template("redeem.html", card_number = request.form["cardnumber"], expiration_date = data["expirationdate"], cvv = request.form["securitycode"] 
        # deposit = data["deposit"])

        card_number = request.form["card_number"]
        expiration_date = request.form["expiration_date"]
        cvv = request.form["cvv"]
        deposit = request.form["deposit"]

        # TODO: actually get the money from ebt to us
        url = "https://sandbox.checkbook.io/v3/check/digital"
        users = supabase.table('Users').select("*").eq("id", user).execute()
        vccs = supabase.table('VCC').select("*").eq("user_id", user).execute()
        user_info = users.data[0]


        payload = {
            "recipient": user_info["email"],
            "name": user_info["name"],
            "amount": float(deposit),
            "description": "redeem EBT"
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": "86a538fb6584799a755f1a2ab03f6d4b:ce2b54a8e93802433632c4c2ac7f4c54"
        }

        response = requests.post(url, json=payload, headers=headers)
        print(response.text)
        res = json.loads(response.text)
        check_id = res["id"]
        
        url = f"https://sandbox.checkbook.io/v3/check/deposit/{check_id}"
        print(url)
        
        payload = {"account": vccs.data[0]["id"]}
        headers = {
            "content-type": "application/json",
            "Authorization": "86a538fb6584799a755f1a2ab03f6d4b:ce2b54a8e93802433632c4c2ac7f4c54"
        }

        response = requests.post(url, json=payload, headers=headers)

        print(response.text)
        # Get current user balance
        buy_product = supabase.table('Users').select("*").eq("id", user).execute()
        user_info = buy_product.data[0]

        # update balance
        _ = supabase.table("Users").update({"balance": int(user_info["balance"]) + int(deposit)}).eq("id", user).execute()

        return redirect(f'/marketplace/{user}')
    else:
        return render_template('error.html')
