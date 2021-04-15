from flask import redirect, url_for, Blueprint, render_template, jsonify
from flask_login import current_user
from junkfood.models import StarredTranscripts
from junkfood import models, db

like_bp = Blueprint('like_bp', __name__)


@like_bp.route('/like/<int:transcript_id>')
def like(transcript_id):
    if not current_user.is_authenticated:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id})
    try:
        models.like_transcript(current_user.id, transcript_id)
    except Exception:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id})
    return jsonify({'result': 'success', 'transcript_id': transcript_id})


@like_bp.route('/unlike/<int:transcript_id>')
def unlike(transcript_id):
    if not current_user.is_authenticated:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id})
    try:
        models.unlike_transcript(current_user.id, transcript_id)
    except Exception:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id})
    return jsonify({'result': 'success', 'transcript_id': transcript_id})
