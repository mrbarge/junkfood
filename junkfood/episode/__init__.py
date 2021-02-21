from flask import redirect, url_for, Blueprint, render_template
from junkfood import models

episode_bp = Blueprint('episode_bp', __name__)


@episode_bp.route('/')
def home():
    episodes = models.get_all_episode_ids()
    return render_template('episode/list.html', episodes=episodes)


@episode_bp.route('/<episodeId>', methods=['GET'])
def view(episodeId):
    episode = models.get_episode(episodeId)
    transcripts = models.get_transcripts(episodeId)
    return render_template('episode/view.html', episode=episode, transcripts=transcripts)
