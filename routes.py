from flask import Flask, render_template, redirect, url_for, session, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
import email_validator
from wtforms.validators import Length, EqualTo, Email, InputRequired
from passlib.handlers.sha2_crypt import sha256_crypt
from database_script import view_posts, view_userinfo
import database_script
from werkzeug.utils import secure_filename

class RegisterationForm(FlaskForm):
    username = StringField('User Name: ', validators = [InputRequired(), Length(min=2, max=50)])
    name = StringField('Name: ', validators = [InputRequired(), Length(min=2, max=100)])
    email = StringField('Email Address: ', validators = [InputRequired(), Email()])
    qualifications = StringField('Qualifications: ', validators = [Length(max=300)])
    interests = StringField('Qualifications: ', validators = [Length(max=300)])
    confirm_password = PasswordField('Confirm Password: ', validators=[InputRequired()])
    password = PasswordField('Password: ', validators = [InputRequired(), Length(min=6), EqualTo('confirm_password')])
    submit = SubmitField("Sign Up")

class SigninForm(FlaskForm):
    username = StringField('Username: ', validators = [InputRequired(), Length(min=2, max=50)])
    password = PasswordField('Password: ', validators = [InputRequired(), Length(min=6)])
    submit = SubmitField("Sign In")

class searchForm(FlaskForm):
    search = StringField('Filter: ', validators = [InputRequired(), Length(max=20)])
    submit = SubmitField("Filter")

class PostForm(FlaskForm):
    title = StringField('Title: ', validators = [InputRequired(), Length(min=2, max=50)])
    description = StringField('Description: ', validators = [Length(max=300)])
    tags = StringField('Tags: ', validators = [Length(max=300)])
    # sell = StringField('To Be Sold or Not: ', validators = [Length(max=300)])
    price = StringField('Price: ', validators = [Length(max=6)])
    submit = SubmitField("Post Artwork")

app = Flask(__name__)
app.config["SECRET_KEY"] = ''
app.config.from_pyfile('config.py')
username = ""
user_level = 0

drone_image_list=["3D_Robotics_Solo.jpg", "DJI_Inspire_1_Pro.jpg", "DJI_Mavic_2_Pro.jpg"
            , "DJI_Matrice_200.jpg", "DJI_Mavic_2_Zoom.jpg", "DJI_Mavic_Air.jpg"
            , "DJI_Mavic_Pro.jpg", "DJI_Phantom_3_Professional.jpg", "DJI_Phantom_4.jpg"
            , "DJI_Spreading_Wings-S900.jpg", "Flyability_Elios_Drone.jpg", "Yuneec_H520.jpg"
            , "Yuneec_Mantis_Q.jpg"]

@app.route('/')
def index_start():
    login = "0"
    try:
        if session["Username"] != None:
            login = "1"
        else:
            login="0"
    except:
        login = "0"
    return redirect(url_for("index", login=login))

@app.route('/index')
def index():
    login = "0"
    try:
        if session["Username"] != None:
            login = "1"
        else:
            login="0"
    except:
        login = "0"
    return render_template("index.html", login=login)

@app.route('/register', methods=["POST", "GET"])
def register():
    database_script.execute_userinfo("CREATE TABLE IF NOT EXISTS userinfo (id INTEGER PRIMARY KEY, profile_pic TEXT, username Text, name TEXT, email TEXT, password TEXT, qualifications TEXT, interests TEXT, plan TEXT)")
    register_form = RegisterationForm()
    errors_lst = []
    user_to_create = {"Username": "", "Name": "", "Email": "", "Password": "", "qualifications": "", "interests": ""}
    rows = database_script.view_userinfo()

    if register_form.validate_on_submit():

        user_to_create = {"Username": register_form.username.data, "Name": register_form.name.data, "Email": register_form.email.data, "Password": sha256_crypt.encrypt(register_form.password.data), "qualifications": register_form.qualifications.data, "interests": register_form.interests.data}

        if rows != [] and rows != None:
            for row in rows:
                if user_to_create["Username"] == row[1]:
                    errors_lst.append("Username: This username is already taken. Please write a different one.")
        
        file = request.files['pfp']
        filename = ""
        print(file.filename, str(file.filename.split(".")[-1]))
        if str(file.filename.split(".")[-1]) in ["png", "jpg", "jpeg"]:
            print("Yes! It reached!")
            filename = "static\\images\\profile_pics\\" + user_to_create["Username"] + "." + str(file.filename.split(".")[-1])
            print(filename)
            file.save(filename)
            print('file uploaded successfully')
        else:
            errors_lst.append("File: " + "Please upload a file with the extention .png, .jpg or .jpeg only")

        print(errors_lst)

            
        if len(errors_lst) == 0:                                                                          
            print(request.files['pfp'])

            user_to_create_command_str = "INSERT INTO userinfo VALUES(NULL, '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (filename, user_to_create["Username"], user_to_create["Name"], user_to_create["Email"], user_to_create["Password"], user_to_create["qualifications"], user_to_create["interests"], "basic")
            database_script.execute_userinfo(user_to_create_command_str)
            session["Username"] = user_to_create["Username"]
            print(view_userinfo())
            return redirect(url_for('profile', login="1"))
            
    if register_form.errors != {}:
        for error_msg, field_name in zip(register_form.errors.values(), register_form.errors.keys()):
            errors_lst.append(field_name[0].upper() + field_name[1:] + ": " + error_msg[0])

    return render_template("register.html", register_form = register_form, errors_lst = errors_lst, login="0")



@app.route('/login', methods=["POST", "GET"])
def signin():
    error_text = ""
    rows = database_script.view_userinfo()
    signin_form = SigninForm()

    if signin_form.validate_on_submit():
        signin_input = [signin_form.username.data, signin_form.password.data]
        for row in rows:
            uname = row[2]
            passwd = row[5]
            if uname == signin_input[0]:
                if sha256_crypt.verify(signin_input[1], passwd):
                    session["Username"] = uname
                    return redirect(url_for('profile', login="1"))

        error_text = "Wrong username or password entered. Please try again."
        
    return render_template("login.html", signin_form=signin_form, error_text = error_text, login="0")



@app.route('/profile', methods=["POST", "GET"])
def profile():
    profile = []
    username = session["Username"]
    rows = database_script.view_userinfo()
    for row in rows:
        if row[2] == username:
            profile = row
    
    print(profile)
    # print('\\'.join(profile[1].split("\\")[1:]))
    # pfp = url_for('static',filename='\\'.join(profile[1].split("\\")[1:]))
    # print(pfp)
    pfp = '/'.join(profile[1].split("\\"))
    print(pfp)
    username = profile[2]
    name = profile[3]
    email = profile[4]
    password = profile[5]
    qualifications = profile[6]
    interests = profile[7]
    plan = profile[8].title()

    # have to put posts and bought sold also here
    # Option to choose the plan
    return render_template("profile.html", login = "1", pfp = pfp, username = username, name = name, email = email, password = password, qualifications = qualifications, interests = interests, plan = plan)

@app.route('/post', methods=["POST", "GET"])
def post():
    if session["Username"] != None:
        post_form = PostForm()
        database_script.execute_userinfo("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY, image TEXT, original_poster Text, title TEXT, description TEXT, tags TEXT, liked_by TEXT, to_sell TEXT, price TEXT, owner TEXT)")
        # Make the form

        errors_lst = []
        rows = database_script.view_posts()

        if post_form.validate_on_submit():

            if str(request.form.get('sell_chekbox')) == "1":
                post_to_create = {"Title": post_form.title.data, "Description": post_form.description.data, "Tags": post_form.tags.data, "To Sell": "yes", "Price": post_form.price.data}
            else:
                post_to_create = {"Title": post_form.title.data, "Description": post_form.description.data, "Tags": post_form.tags.data, "To Sell": "no", "Price": ""}

            print(post_to_create)

            if rows != [] and rows != None:
                for row in rows:
                    if post_to_create["Title"] == row[3]:
                        errors_lst.append("Title: This title is already taken. Please choose a different one.")
            
            file = request.files['post']
            filename = ""
            print(file.filename, str(file.filename.split(".")[-1]))
            if str(file.filename.split(".")[-1]) in ["png", "jpg", "jpeg"]:
                print("Yes! It reached!")
                filename = "static\\images\\posts\\" + post_to_create["Title"] + "." + str(file.filename.split(".")[-1])
                print(filename)
                file.save(filename)
                print('file uploaded successfully')
            else:
                errors_lst.append("File: " + "Please upload a file with the extention .png, .jpg or .jpeg only")

            print(errors_lst)

                
            if len(errors_lst) == 0:                                                                          
                print(request.files['post'])

                post_to_create_command = "INSERT INTO posts VALUES(NULL, '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format('/'.join(filename.split("\\")), str(session["Username"]), post_to_create["Title"], post_to_create["Description"], post_to_create["Tags"], '', post_to_create["To Sell"], post_to_create["Price"], '')

                # post_to_create_command = "INSERT INTO posts VALUES(NULL, '" + str(filename) + "', '" + str(session["Username"]) + "', '" + post_to_create["Title"] + "', '" + post_to_create["Description"] + "', '" + post_to_create["Tags"] + "', '', '" + post_to_create["To Sell"] + "', '" + post_to_create["Price"] + "', '')"

                # post_to_create_command = "INSERT INTO posts VALUES(NULL, '%s', '%s', '%s', '%s', '%s', '', '%s', '%s', '')" % (filename, str(session["Username"]), post_to_create["Title"], post_to_create["Description"], post_to_create["Tags"], post_to_create["To Sell"], post_to_create["Price"])
                print(post_to_create_command)
                database_script.execute_userinfo(post_to_create_command)
                print(view_posts())
                return redirect(url_for('index', login="1"))

        if post_form.errors != {}:
            for error_msg, field_name in zip(post_form.errors.values(), post_form.errors.keys()):
                errors_lst.append(field_name[0].upper() + field_name[1:] + ": " + error_msg[0])

        return render_template("post.html", login = "1", post_form = post_form, errors_lst = errors_lst)

    else:
        return render_template("index.html", login = "0")


@app.route('/community', methods=["POST", "GET"])
def community():
    try:
        if session["Username"] != None:
            login = "1"
        else:
            login="0"
    except:
        login = "0"
    
    rows = view_posts()
    print(rows)
    lst = []
    for row in rows:
        if row[7] == "yes":
            lst.append({"post": row[1], "owner": row[2], "title": row[3], "description": row[4], "tags": row[5], "price": row[8]})
        elif row[7] == "no":
            lst.append({"post": row[1], "owner": row[2], "title": row[3], "description": row[4], "tags": row[5], "price": "Not for sale"})

        # lst.append({"post": row[1], "owner": row[2], "title": row[3], "description": row[4], "tags": row[5], "price": "Not for sale"})

    print(lst)
    return render_template("community.html", login = login, rows = lst)


# Number of likes





@app.route('/signout')
def signout():
    session["Username"] = None
    return render_template("index.html", login="0")


if __name__ == "__main__":
    app.run(debug=True, port=1111)
