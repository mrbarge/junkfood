import traceback

from flask import Flask, render_template, Blueprint, current_app, jsonify

from junkfood import db
from junkfood.exceptions import ApplicationError

error_bp = Blueprint('error', __name__)


@current_app.errorhandler(404)
def not_found(e):
    return render_template('error/404.html')


@current_app.errorhandler(ApplicationError)
def handle_error(error):
    db.session.rollback()
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@current_app.errorhandler(Exception)
def general_exception(e):
    print(e)
    print(traceback.format_exc())
    return render_template('error/error.html')
