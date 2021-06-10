import sqlalchemy
import validators
from flask import redirect, Blueprint, abort, url_for, current_app, flash
from flask_login import current_user
from junkfood.exceptions import ApplicationError
from junkfood.models import Episode

media_bp = Blueprint('media_bp', __name__)


@media_bp.route('/<int:show_id>/<episodeNumber>')
def get(show_id, episodeNumber):
    current_app.logger.info(f'requesting show:{show_id} episode:{episodeNumber}')
    try:
        episode = Episode.query.filter(Episode.show == show_id, Episode.episode == episodeNumber).first()

        if not episode:
            raise ApplicationError(f'Unable to retrieve episode.', status_code=404)

        # If the media field is a URL, just redirect there
        if validators.url(episode.media):
            return redirect(episode.media)

        # Otherwise assume it's a local path, only allow that for authenticated users
        if not current_user.is_authenticated:
            abort(400)

        return redirect(url_for('protected_bp.protected', filename=episode.media))

    except sqlalchemy.exc.SQLAlchemyError as err:
        current_app.logger.error(f'unable to load media: {err}')
        raise ApplicationError(f'Unable to retrieve media.', status_code=500)
