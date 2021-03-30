import json
from flask import redirect, url_for, Blueprint, render_template, request, Response
from junkfood.search.forms import SearchForm
from junkfood import models

search_bp = Blueprint('search_bp', __name__)


@search_bp.route('/_autocomplete')
def autocomplete():
    try:
        search = request.args.get('q')
        terms = search.split()
        if terms[-1] == 'speaker:':
            speakers = models.get_speakers()
            retdata = {
                'matching_results': [' '.join(terms[:-1] + [f'speaker:{s[0]}']) for s in speakers]
            }
            return Response(json.dumps(retdata), mimetype='application/json')
        return Response(json.dumps('{"matching_results": []}'), mimetype='application/json')
    except Exception as err:
        print(err)
        return Response(json.dumps('{"matching_results": []}'), mimetype='application/json')


@search_bp.route('/', methods=['GET', 'POST'])
def search():
    search_form = SearchForm()
    matches = []

    if request.method == 'POST':
        if search_form.validate():
            query = search_form.search.data
            matches = models.search(query)

    return render_template('search/search.html', form=search_form, matches=matches)
