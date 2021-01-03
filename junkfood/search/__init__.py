from flask import redirect, url_for, Blueprint, render_template, request
from junkfood.search.forms import SearchForm
from junkfood import models

search_bp = Blueprint('search_bp', __name__)


@search_bp.route('/', methods=['GET','POST'])
def search():
    search_form = SearchForm()
    search_form.speakers.choices = [("", "---")] + models.get_speakers()
    matches = []

    if request.method == 'POST':
        if search_form.validate():
            speaker = search_form.speakers.data
            episode = search_form.episode.data
            transcript = search_form.transcript.data

            matches = models.search(transcript, episode, speaker)

    return render_template('search/search.html', form=search_form, matches=matches)
