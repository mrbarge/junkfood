import os.path
import traceback
import validators
from flask import redirect, url_for, Blueprint, render_template, jsonify, flash, send_from_directory, current_app, abort
from flask_login import current_user
from junkfood import models, db

media_bp = Blueprint('media_bp', __name__)


@media_bp.route('/<int:show_id>/<episodeNumber>')
def get(show_id, episodeNumber):
    try:
        episode = models.get_episode(show_id, episodeNumber)

        # If the media field is a URL, just redirect there
        if validators.url(episode.media):
            return redirect(episode.media)

        # Otherwise assume it's a local path, only allow that for authenticated users
        if not current_user.is_authenticated:
            abort(400)
        return send_from_directory('static', filename=episode.media)

    except Exception as err:
        abort(500)
