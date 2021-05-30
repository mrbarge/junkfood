import sqlalchemy
from flask import Blueprint, render_template, current_app
from flask_login import current_user
from sqlalchemy.sql.expression import func as sqlfunc, desc
from junkfood.exceptions import ApplicationError
from junkfood.models import Show, Episode, Transcript, TermFrequency, Terms, StarredTranscripts

episode_bp = Blueprint('episode_bp', __name__)


@episode_bp.route('/')
def home():
    try:
        shows = Show.query.all()
        return render_template('episode/shows.html', shows=shows)
    except sqlalchemy.exc.SQLAlchemyError:
        raise ApplicationError('Unable to list available shows.', status_code=500)


@episode_bp.route('/<show_title>')
def show_home(show_title):
    try:
        show = Show.query.filter(Show.title == show_title).first()
        episodes = Episode.query.filter(Episode.show == show.id).order_by(desc(Episode.date)).all()
        return render_template('episode/episodes.html', show=show, episodes=episodes)
    except sqlalchemy.exc.SQLAlchemyError:
        raise ApplicationError(f'Unable to list episodes available for {show_title}.', status_code=500)


@episode_bp.route('/<show_title>/<episode_number>', methods=['GET'], defaults={'timecode': '0'})
@episode_bp.route('/<show_title>/<episode_number>/<timecode>', methods=['GET'])
def view(show_title, episode_number, timecode):
    try:
        show = Show.query.filter(Show.title == show_title).first_or_404()
        episode = Episode.query.filter(Episode.show == show.id, Episode.episode == episode_number).first_or_404()
        transcripts = Transcript.query.filter(Transcript.episode == episode.id).order_by(Transcript.index)

        all_terms = TermFrequency.query.join(Terms).add_columns(Terms.id, Terms.term, Terms.label).filter(
            TermFrequency.episode_id == episode.id).order_by(TermFrequency.freq.desc()).limit(
            current_app.config['TERMS_PER_EPISODE'])
        top_terms = [{
            'id': term[1],
            'term': term[2],
            'label': term[3],
            'freq': term[0].freq
        } for term in all_terms]
        transcript_ids = [x.id for x in transcripts]

        transcript_stars = []
        if current_user.is_authenticated:
            episode_stars = StarredTranscripts.query.filter(StarredTranscripts.user_id == current_user.id,
                                                            StarredTranscripts.transcript_id.in_(transcript_ids))
            transcript_stars = [row.transcript_id for row in episode_stars]

        return render_template('episode/view.html', episode=episode, show=show, transcripts=transcripts,
                               timecode=timecode,
                               stars=transcript_stars, terms=top_terms)
    except sqlalchemy.exc.SQLAlchemyError:
        raise ApplicationError(f'Unable to view episode.', status_code=500)


@episode_bp.route('/random', methods=['GET'])
def random():
    try:
        episode = Episode.query.filter().order_by(sqlfunc.random()).first()
        show = Show.query.filter(Show.id == episode.show).first_or_404()
        return view(show.title, episode.episode, 0)
    except sqlalchemy.exc.SQLAlchemyError:
        raise ApplicationError(f'Unable to view random episode.', status_code=500)
