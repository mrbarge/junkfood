from junkfood.auth.forms import LoginForm, RegisterForm, ResetPasswordForm, SetPasswordForm
from junkfood.models import User, Role, RoleAssociation
from flask import Blueprint, redirect, url_for, request, flash, render_template, current_app
from flask_login import login_required, logout_user, current_user, login_user, login_manager
from junkfood.models import db
from itsdangerous import URLSafeTimedSerializer

# Blueprint Configuration
auth_bp = Blueprint(
    'auth_bp', __name__,
    template_folder='templates',
    static_folder='static', static_url_path='assets')

ts = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('base_bp.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('Invalid username/password combination')
            return redirect(url_for('auth_bp.login'))

        if not user.email_confirmed:
            flash('User email not confirmed. Please check your email for a confirmation link.')
            return redirect(url_for('auth_bp.login'))

        if user.check_password(password=form.password.data):
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

        token = ts.dumps(form.email.data, salt='email-confirm-key')
        confirm_url = url_for(
            'auth_bp.confirm_email',
            token=token,
            _external=True)
        html = render_template(
            'auth/activate.html',
            confirm_url=confirm_url)
        print(html)

        flash(f'A confirmation email has been sent to "{form.email.data}".')
        return redirect(url_for('auth_bp.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('base_bp.home'))


@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = ts.loads(token, salt="email-confirm-key", max_age=86400)
    except:
        flash('Token is not valid or has expired.')
        return redirect(url_for('auth_bp.register'))

    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User does not exist.')
        return redirect(url_for('auth_bp.register'))

    user.email_confirmed = True
    db.session.commit()
    flash(f'User account for email address "{email}" confirmed, you may now log in.')
    return redirect(url_for('auth_bp.login'))


@auth_bp.route('/reset', methods=["GET", "POST"])
def reset():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first_or_404()

        subject = "Password reset requested"

        token = ts.dumps(form.email.data, salt='recover-key')

        recover_url = url_for(
            'auth_bp.reset_with_token',
            token=token,
            _external=True)

        html = render_template(
            'auth/recover.html',
            recover_url=recover_url)

        print(html)
        flash('Please check your email for a password reset link.')
        return redirect(url_for('base_bp.home'))
    return render_template('auth/reset.html', form=form)


@auth_bp.route('/reset/<token>', methods=["GET", "POST"])
def reset_with_token(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        flash('Token is not valid or has expired.')
        return redirect(url_for('auth_bp.reset'))

    form = SetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first_or_404()
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password has been reset, you may now login.')
        return redirect(url_for('auth_bp.login'))

    return render_template('auth/reset_with_token.html', form=form, token=token)