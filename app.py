"""Flask Feedback Application."""

from flask import Flask, redirect, render_template, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm, DeleteForm
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "shhhhh...secret"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)

toolbar = DebugToolbarExtension(app)


#############################################
# ROUTES:
#############################################


@app.route('/')
def root_route():
    """Root route."""
    return redirect("/login")


@app.route('/register', methods=["GET", "POST"])
def register_new_user():
    """Show registration form to register/create a user."""
    
    
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        user = User.register(username, password, email, first_name, last_name)

        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username taken. Please enter another username.")
        session['username'] = user.username
        flash(f"Welcome, {user.username}! Account successfully created!", 'success')
        return redirect(f"/users/{user.username}")
    return render_template("register.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login_user():
    """Shows Login form or handles Login of user."""

    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)
        if user:
            flash(f"Welcome back, {user.username}!", 'info')
            session["username"] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password combination.']
    return render_template('login.html', form=form)



@app.route('/logout')
def logout_user():
    session.pop('username')
    flash("Goodbye!", 'info')
    return redirect('/')


@app.route('/users/<username>')
def show_user_page(username):
    """Shows userpage upon login authentication."""
        
    user = User.query.get_or_404(username)
    form = DeleteForm()
 
    return render_template('user.html', user=user, form=form)


@app.route('/users/<username>/delete', methods=["POST"])
def delete_user(username):
    """Delete user and redirect to login."""
    
    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    return redirect("/login")


@app.route("/users/<username>/feedback/add", methods=["GET", "POST"])
def add_feedback(username):
    """Show Feedback Form and handle submission."""
    if "username" not in session or username != session['username']:
        raise NameError("Please Login.")

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        feedback = Feedback(title=title, content=content, username=username)
        
        db.session.add(feedback)
        db.session.commit()
        return redirect(f"/users/{feedback.username}")
    else:
        return render_template("add_feedback.html", form=form)


@app.route('/feedback/<int:feedback_id>/edit', methods=["GET", "POST"])
def edit_feedback(feedback_id):    
    """Show Edit Feedback form and handle submission."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise NameError("Please Login.")

    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        return redirect(f"/users/{feedback.username}")

    return render_template("edit_feedback.html", form=form, feedback=feedback)



@app.route('/feedback/<int:feedback_id>/delete', methods=["POST"])
def delete_feedback(feedback_id):
    """Delete feedback."""

    feedback = Feedback.query.get(feedback_id)

    if "username" not in session or feedback.username != session['username']:
        raise NameError("Please Login.")

    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
    
    return redirect(f"/users/{feedback.username}")
