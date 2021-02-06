import sqlalchemy
from flask import Flask, render_template, abort, session, redirect, request
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash 


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:admin@localhost/flask_blog"
app.config['SECRET_KEY'] = "mysecretkeywhichisnotsecretrightnow"
db=SQLAlchemy(app)
admin = Admin(app)
Ckeditor = CKEditor(app)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    subtitle=db.Column(db.String(100))
    author = db.Column(db.String(30))
    content=db.Column(db.Text(500))
    date_posted = db.Column(db.DateTime)
    slug = db.Column(db.String(100))

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(500))
    password_hash = db.Column(db.String(500))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class SecureModelView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)

admin.add_view(SecureModelView(Posts, db.session))
admin.add_view(SecureModelView(Users, db.session))

@app.route('/')
def hello():
    posts=Posts.query.all()
    return render_template('index.html', posts=posts)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/post/<string:slug>')
def post(slug):
    try:
        post = Posts.query.filter_by(slug=slug).one()
        return render_template('post.html', post=post)
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user_data = Users.query.filter_by(username=username).first()
        if user_data != None and user_data.check_password(password):
            return redirect('/admin')
            session.logged_in = True
        else:
            abort(403)

    return render_template("login.html")

@app.route('/logout')
def logout():
   session.clear()
   return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)