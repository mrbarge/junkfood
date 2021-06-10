import os

from flask import Blueprint, send_from_directory, current_app
from flask_login import login_required

protected_bp = Blueprint('protected_bp', __name__)


@protected_bp.route('/<path:filename>')
@login_required
def protected(filename):
    current_app.logger.info(f'requested protected file: {filename}')
    return send_from_directory(
        os.path.dirname(__file__),
        filename
    )
