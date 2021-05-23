from flask import Blueprint, render_template, current_app
from flask_login import current_user
from junkfood import models


episode_bp = Blueprint('episode_bp', __name__)



@episode_bp.route('/')
def home():
    shows = models.get_all_shows()
    return render_template('episode/list_shows.html', shows=shows)


@episode_bp.route('/<showTitle>')
def show_home(showTitle):
    episodes = models.get_all_episode_numbers(showTitle)
    return render_template('episode/list_episodes.html', showTitle=showTitle, episodes=episodes)


@episode_bp.route('/<showTitle>/<episodeNumber>', methods=['GET'], defaults={'timecode': '0'})
@episode_bp.route('/<showTitle>/episodeNumber>/<timecode>', methods=['GET'])
def view(showTitle, episodeNumber, timecode):
    show = models.get_show_by_title(showTitle)
    episode = models.get_episode(show.id, episodeNumber)
    transcripts = models.get_transcripts(episode.id)
    terms = models.get_terms_for_episode(episode.id, current_app.config['TERMS_PER_EPISODE'])
    transcript_stars = []
    if current_user.is_authenticated:
        transcript_stars = models.get_stars(current_user.id, episode.id)
    return render_template('episode/view.html', episode=episode, show=show, transcripts=transcripts, timecode=timecode, stars=transcript_stars, terms=terms)


@episode_bp.route('/random', methods=['GET'])
def random():
    episode = models.get_random_episode()
    show = models.get_show(episode.show)
    return view(show.title, episode.episode, 0)
