from junkfood.auth.forms import LoginForm
from junkfood.models import User
from flask import Blueprint, redirect, url_for, request, flash, render_template
from flask_login import login_required, logout_user, current_user, login_user, login_manager

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


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth_bp.login'))
