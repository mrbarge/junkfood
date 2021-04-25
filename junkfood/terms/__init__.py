from flask import Blueprint, render_template
from junkfood import models

term_bp = Blueprint('terms_bp', __name__)


@term_bp.route('/')
def home():
    terms = models.top_terms(30)
    return render_template('terms/list.html', terms=terms)


@term_bp.route('/<int:termId>', methods=['GET'])
def view(termId):
    term = models.Terms.query.filter(models.Terms.id == termId).first_or_404()
    episodes = models.get_episodes_for_term(termId)
    return render_template('terms/view.html', term=term, episodes=episodes)
