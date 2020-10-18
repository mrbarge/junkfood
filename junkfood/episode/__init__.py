from flask import redirect, url_for, Blueprint, render_template
from junkfood import models

episode_bp = Blueprint('episode_bp', __name__)


@episode_bp.route('/')
def home():
    episodes = models.get_episodes()
    return render_template('episode/list.html', episodes=episodes)
