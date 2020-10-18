from flask import redirect, url_for, Blueprint, render_template


base_bp = Blueprint('base_bp', __name__)


@base_bp.route('/')
def base():
    return render_template('base/home.html')
