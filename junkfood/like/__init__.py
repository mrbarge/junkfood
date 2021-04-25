from flask import redirect, url_for, Blueprint, render_template, jsonify, flash
from flask_login import current_user
from junkfood import models, db

like_bp = Blueprint('like_bp', __name__)


@like_bp.route('/like/<int:transcript_id>')
def like(transcript_id):
    if not current_user.is_authenticated:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 401
    try:
        models.like_transcript(current_user.id, transcript_id)
    except Exception:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 500
    return jsonify({'result': 'success', 'transcript_id': transcript_id})


@like_bp.route('/unlike/<int:transcript_id>')
def unlike(transcript_id):
    if not current_user.is_authenticated:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 401
    try:
        models.unlike_transcript(current_user.id, transcript_id)
    except Exception:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 500
    return jsonify({'result': 'success', 'transcript_id': transcript_id})


@like_bp.route('/my_likes')
def my_likes():
    if not current_user.is_authenticated:
        flash('You must be logged in to view this feature.')
        return redirect(url_for('base_bp.home'))
    try:
        matches = models.my_likes(current_user.id)
        tops = models.top_likes()
        return render_template('like/my_likes.html', matches=matches)
    except Exception as e:
        flash('Unable to retrieve user favourites.')
    return redirect(url_for('base_bp.home'))


@like_bp.route('/all_time')
def all_time():
    try:
        matches = models.top_likes()
        classics = models.classics()
        print(classics)
        return render_template('like/all_time.html', matches=matches)
    except Exception as e:
        print(e)
        flash('Unable to retrieve user favourites.')
    return redirect(url_for('base_bp.home'))


@like_bp.route('/classics')
def classics():
    try:
        matches = models.classics()
        return render_template('like/classics.html', matches=matches)
    except Exception as e:
        flash('Unable to retrieve user favourites.')
    return redirect(url_for('base_bp.home'))
