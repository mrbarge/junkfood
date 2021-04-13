from junkfood.auth.forms import LoginForm, RegisterForm
from junkfood.models import User, Role, RoleAssociation
from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_required, logout_user, current_user, login_user, login_manager
from junkfood.models import db

# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base_bp.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('base_bp.home'))
        flash('Invalid username/password combination')
        return redirect(url_for('auth_bp.login'))
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('base_bp.home'))

    form = RegisterForm()
    if form.validate_on_submit():
        user_exists = User.query.filter_by(email=form.email.data).first()
        if user_exists:
            flash('User already exists.')
            return redirect(url_for('auth_bp.register'))

        newuser = User(email=form.email.data)
        newuser.set_password(form.password.data)
        db.session.add(newuser)

        role = Role.query.filter_by(role=Role.PREMIUM).first()
        user_role = RoleAssociation(user_id=newuser.id, role_id=role.id)
        db.session.add(user_role)
        db.session.commit()

        login_user(newuser)
        return redirect(url_for('base_bp.home'))
    return render_template('auth/register.html', form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_bp.home'))
