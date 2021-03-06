# -*- coding: utf-8 -*-

from scripts import tabledef
from scripts import forms
from scripts import helpers
from flask import Flask, redirect, url_for, render_template, request, session
import json
import sys
import os
import time
import random
import shutil
import ml.code.diagnosis
import ml.code.utils
import stripe

app = Flask(__name__)
app.secret_key = os.urandom(12)  # Generic key for dev purposes only

stripe_keys = {
  'secret_key': os.environ['STRIPE_SECRET_KEY'],
  'publishable_key': os.environ['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = stripe_keys['secret_key']


# Heroku
#from flask_heroku import Heroku
#heroku = Heroku(app)

# ======== Routing =========================================================== #
# -------- Login ------------------------------------------------------------- #
@app.route('/', methods=['GET', 'POST'])
def login():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = request.form['password']
            if form.validate():
                if helpers.credentials_valid(username, password):
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Login successful'})
                return json.dumps({'status': 'Invalid user/pass'})
            return json.dumps({'status': 'Both fields required'})
        return render_template('login.html', form=form)
    user = helpers.get_user()
    return render_template('pneumonia.html', user=user)


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('login'))


# -------- Signup ---------------------------------------------------------- #
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not session.get('logged_in'):
        form = forms.LoginForm(request.form)
        if request.method == 'POST':
            username = request.form['username'].lower()
            password = helpers.hash_password(request.form['password'])
            email = request.form['email']
            if form.validate():
                if not helpers.username_taken(username):
                    helpers.add_user(username, password, email)
                    session['logged_in'] = True
                    session['username'] = username
                    return json.dumps({'status': 'Signup successful'})
                return json.dumps({'status': 'Username taken'})
            return json.dumps({'status': 'User/Pass required'})
        return render_template('login.html', form=form)
    return redirect(url_for('login'))


# -------- Settings ---------------------------------------------------------- #
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('settings.html', user=user)
    return redirect(url_for('login'))

# -------- Pneumonia ---------------------------------------------------------- #
@app.route('/pneumonia', methods=['POST'])
def pneumonia():
    if session.get('logged_in'):
        if request.method == 'POST':
            password = request.form['password']
            if password != "":
                password = helpers.hash_password(password)
            email = request.form['email']
            helpers.change_user(password=password, email=email)
            return json.dumps({'status': 'Saved'})
        user = helpers.get_user()
        return render_template('pneumonia.html', user=user)
    return redirect(url_for('login'))


# -------- Upload ---------------------------------------------------------- #
@app.route('/upload', methods=['POST'])
def upload():
    APP_ROOT = os.path.dirname(os.path.abspath(__file__))
    print("APP_ROOT:" + APP_ROOT)
    # folder_name = request.form['superhero']
    folder_name = "./ml/data/input/test/" + str(time.time()) + "." + str(random.randint(111111, 999999))
    # create this folder
    ml.code.utils.mkdir_p(folder_name + "/NORMAL")
    ml.code.utils.mkdir_p(folder_name + "/PNEUMONIA")
    folder_name_normal = folder_name + "/NORMAL"

    '''
    # this is to verify that folder to upload to exists.
    if os.path.isdir(os.path.join(APP_ROOT, '/{}'.format(folder_name))):
        print("folder exist")
    '''
    print("Current Directory:" + str(os.getcwd()))
    # target = os.path.join(APP_ROOT, '/{}'.format(folder_name_normal))
    target = folder_name_normal
    print("TargetFolder:" + target)
    if not os.path.isdir(target):
        os.mkdir(target)
    print(request.files.getlist("file"))
    for upload in request.files.getlist("file"):
        # print("Upload File:" + upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        print("Filename:" + filename)
        # This is to verify files are supported
        ext = os.path.splitext(filename)[1]
        print("Extension:" + ext)
        if (ext == ".jpg") or (ext == ".png") or (ext == ".jpeg"):
            print("File supported moving on...")
        else:
            render_template("Error.html", message="Files uploaded are not supported...")
        destination = "/".join([target, filename])
        print("Accept incoming file:", filename)
        print("Save it to:", destination)
        upload.save(destination)
        session['folder_name'] = folder_name

    # return send_from_directory("images", filename, as_attachment=True)    
    # return render_template("processImage.html", folder_name=folder_name)
    return render_template("stripeIndex.html", key=stripe_keys['publishable_key'])


@app.route('/stripeCharge', methods=['POST'])
def stripeCharge():
    try:
        amount = 500   # amount in cents
        customer = stripe.Customer.create(
            email='sample@customer.com',
            source=request.form['stripeToken']
        )
        stripe.Charge.create(
            customer=customer.id,
            amount=amount,
            currency='usd',
            description='Diagnosis Charge'
        )
        return render_template('stripeCharge.html', amount=amount)
    except stripe.error.StripeError:
        return render_template('stripeError.html')




# -------- Process ---------------------------------------------------------- #
@app.route('/process', methods=['POST'])
def process():
    folder_name = session['folder_name']
    # try:
    diag = ml.code.diagnosis.get_diagnosis(folder_name)
    # except:
        # diag = 9999

    # print("Returned Value:" + str(diag))
    # return("<h1>Processed Image " + folder_name + 
    #        "<br>Yahooooooooooooooooooooooo" +
    #        "<br>Diagnosis:" + str(diag) + "</h1>")

    # delete folder
    shutil.rmtree(folder_name)

    # remove session value
    session.pop('folder_name', None)  
    
    return render_template("processResult.html", folder_name=folder_name+"/NORMAL", diag=diag)


# ======== Main ============================================================== #
if __name__ == "__main__":
    app.run(debug=True, use_reloader=True)
