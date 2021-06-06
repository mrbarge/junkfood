import sqlalchemy
from flask import Blueprint, render_template
from sqlalchemy import func, desc
from junkfood import models, db
from junkfood.exceptions import ApplicationError
from junkfood.models import TermFrequency, Terms, Episode, Show

term_bp = Blueprint('terms_bp', __name__)


@term_bp.route('/')
def home():
    try:
        all_terms = TermFrequency.query.with_entities(TermFrequency.term_id,
                                                      func.count(TermFrequency.freq).label('freq')).group_by(
            TermFrequency.term_id).order_by(desc('freq')).limit(30)
        terms = [Terms.query.filter(Terms.id == t[0]).first() for t in all_terms]
        return render_template('terms/list.html', terms=terms)
    except sqlalchemy.exc.SQLAlchemyError:
        raise ApplicationError('Unable to fetch list of terms', status_code=500)


@term_bp.route('/<term_id>', methods=['GET'])
def view(term_id):
    try:
        term = models.Terms.query.filter(models.Terms.id == term_id).first_or_404()
        all_episodes = db.session.query(TermFrequency, Episode, Show).filter(
            TermFrequency.episode_id == Episode.id,
            Episode.show == Show.id,
            TermFrequency.term_id == term.id
        ).order_by(TermFrequency.freq.desc()).limit(20)

        top_episodes = [{
            'episodeNumber': ep.Episode.episode,
            'showTitle': ep.Show.title,
            'freq': ep.TermFrequency.freq,
        } for ep in all_episodes]
        return render_template('terms/view.html', term=term, episodes=top_episodes)
    except sqlalchemy.exc.SQLAlchemyError:
        raise ApplicationError('Unable to fetch episodes relating to term', status_code=500)
