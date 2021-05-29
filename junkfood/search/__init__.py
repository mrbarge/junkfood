import json
from flask import redirect, url_for, Blueprint, render_template, request, Response, current_app
from sqlalchemy import func

from junkfood.models import Transcript
from junkfood.search.forms import SearchForm
from junkfood import models

search_bp = Blueprint('search_bp', __name__)


@search_bp.route('/_autocomplete')
def autocomplete():
    try:
        search = request.args.get('q')
        terms = search.split()
        if terms[-1] == 'speaker:':
            speakers = get_speakers()
            retdata = {
                'matching_results': [' '.join(terms[:-1] + [f'speaker:{s[0]}']) for s in speakers]
            }
            return Response(json.dumps(retdata), mimetype='application/json')
        return Response(json.dumps('{"matching_results": []}'), mimetype='application/json')
    except Exception as err:
        print(err)
        return Response(json.dumps('{"matching_results": []}'), mimetype='application/json')


@search_bp.route('/', methods=['GET', 'POST'])
@search_bp.route('/<int:page>/<search>', methods=['GET', 'POST'])
def search(page=None, search=None):
    search_form = SearchForm()
    matches = []

    if request.method == 'POST':
        search = request.form.get("search")
        page = request.args.get('page', 1, type=int)
        return redirect(url_for('search_bp.search', page=page, search=search))

    if page is not None and search is not None:
        matches = models.search(search, page, current_app.config['ITEMS_PER_PAGE'], current_app.config['MAX_SEARCH_RESULTS'])
        return render_template('search/search.html', form=search_form, matches=matches, search=search)

    return render_template('search/search.html', form=search_form, matches=matches)


def get_speakers():
    '''
    Retrieve all speakers
    :return: List of speaker tuples (value,presented name)
    '''
    all_speakers = Transcript.query.with_entities(Transcript.speaker,
                                                  func.count(Transcript.speaker).label('total')).filter(
        ~Transcript.speaker.startswith('Unknown')).group_by(
        Transcript.speaker).order_by(desc('total'))
    speakers = [x.speaker for x in all_speakers]
    return speakers


