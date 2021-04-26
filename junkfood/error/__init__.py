import traceback

from flask import Flask, render_template, Blueprint, current_app

error_bp = Blueprint('error', __name__)


@current_app.errorhandler(404)
def not_found(e):
    print(e)
    return render_template('error/404.html')


@current_app.errorhandler(Exception)
def general_exception(e):
    print(e)
    print(traceback.format_exc())
    return render_template('error/error.html')
