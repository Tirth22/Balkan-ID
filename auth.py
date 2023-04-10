import csv
from flask import jsonify, send_file
import requests
import psycopg2


try:
    from flask import Flask,render_template,url_for,request,redirect, make_response
    from time import time
    from random import random
    from flask import Flask, render_template, make_response
    from flask_dance.contrib.github import make_github_blueprint, github
    import cache
    import os 
except Exception as e:
    print("Some Modules are Missings {}".format(e))


app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"
app.secret_key = "super secret key"

@app.route("/")
def index():
    return render_template('index.html')

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

github_blueprint = make_github_blueprint(client_id='8256745143424682257e',
                                         client_secret='f1c1f69da55f1b692c5faac47f579d40f8c5f099')

app.register_blueprint(github_blueprint, url_prefix='/github_login')




@app.route('/login',methods=['GET'])

def login():
    if not github.authorized:
        return redirect(url_for('github.login'))
    else:
        account_info = github.get('/user')
        if account_info.ok:
            account_info_json = account_info.json()
            username = account_info_json['login']
            #return '<h1>Your Github name is {}'.format(account_info_json)
        
    # GitHub API endpoint to retrieve information about a user's repositories
    url = 'https://api.github.com/users/'+username+'/repos'

    # Replace <username> with the GitHub username you want to retrieve data for
    response = requests.get(url)


    for repo in response.json():
        owner_id = repo['owner']['id']
        owner_name = repo['owner']['login']
        owner_email = repo['owner'].get('email', '')
        repo_id = repo['id']
        repo_name = repo['name']
        status = 'Public' if repo['private'] == False else 'Private'
        stars_count = repo['stargazers_count']
        

    conn = psycopg2.connect(
        host="localhost",
        database="balkan_id",
        user="postgres",
        password="tirth123"
    )

    # Retrieve data from request
    data = request.form
    
    # Insert data into database
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO  user_det
        VALUES (%s, %s,%s)
    """, (account_info_json['id'], account_info_json['login'], account_info_json['node_id']))
    
    if not conn.commit():
        pass

    conn2 = psycopg2.connect(
        host="localhost",
        database="balkan_id",
        user="postgres",
        password="tirth123"
    )

    # Retrieve data from request
    data2 = request.form
    
    # Insert data into database
    cursor2 = conn.cursor()
    cursor2.execute("""
        INSERT INTO  repo_details
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (owner_id,owner_email,repo_id,repo_name,status,stars_count))
    conn2.commit()
    
    # Return success message
    return render_template('fetch.html')






    

@app.route('/download',methods=['GET'])

def download():
        
    conn = psycopg2.connect(
        host="localhost",
        database="balkan_id",
        user="postgres",
        password="tirth123"
    )
    cur = conn.cursor()
    cur.execute("SELECT * FROM repo_details")
    rows = cur.fetchall()

    with open('data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for row in rows:
            writer.writerow(row)

    conn.close()

    return send_file('data.csv', as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
    cache.init_app(app) 