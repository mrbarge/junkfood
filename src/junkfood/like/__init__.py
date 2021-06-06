import sqlalchemy
from flask import redirect, url_for, Blueprint, render_template, jsonify, flash
from flask_login import current_user
from sqlalchemy import func, desc

from junkfood import db
from junkfood.models import StarredTranscripts, Transcript, Episode, Show, Classics

like_bp = Blueprint('like_bp', __name__)


@like_bp.route('/like/<int:transcript_id>')
def like(transcript_id):
    if not current_user.is_authenticated:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 401
    try:
        user_star = StarredTranscripts(user_id=current_user.id, transcript_id=transcript_id)
        db.session.add(user_star)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as err:
        print(err)
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 500
    return jsonify({'result': 'success', 'transcript_id': transcript_id})


@like_bp.route('/unlike/<int:transcript_id>')
def unlike(transcript_id):
    if not current_user.is_authenticated:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 401
    try:
        StarredTranscripts.query.filter(StarredTranscripts.user_id == current_user.id,
                                        StarredTranscripts.transcript_id == transcript_id).delete()
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError:
        return jsonify({'result': 'failed', 'transcript_id': transcript_id}), 500
    return jsonify({'result': 'success', 'transcript_id': transcript_id})


@like_bp.route('/my_likes')
def my_likes():
    if not current_user.is_authenticated:
        flash('You must be logged in to view this feature.')
        return redirect(url_for('base_bp.home'))
    try:
        likes = StarredTranscripts.query.filter(StarredTranscripts.user_id == current_user.id)
        like_transcripts = [x.transcript_id for x in likes]
        transcripts = db.session.query(Transcript, Episode, Show).filter(
            Transcript.episode == Episode.id,
            Episode.show == Show.id,
            Transcript.id.in_(like_transcripts)).all()
        return render_template('like/my_likes.html', matches=transcripts)
    except sqlalchemy.exc.SQLAlchemyError:
        flash('Unable to retrieve user favourites.')
    return redirect(url_for('base_bp.home'))


@like_bp.route('/all_time')
def all_time():
    try:
        top_likes = StarredTranscripts.query.with_entities(StarredTranscripts.transcript_id,
                                                           func.count(StarredTranscripts.transcript_id).label(
                                                               'count')).group_by(
            StarredTranscripts.transcript_id).order_by(desc('count')).limit(20).all()
        like_transcripts = [x.transcript_id for x in top_likes]
        transcripts = db.session.query(Transcript, Episode, Show).filter(
            Transcript.episode == Episode.id,
            Episode.show == Show.id,
            Transcript.id.in_(like_transcripts)).all()
        return render_template('like/all_time.html', matches=transcripts)
    except sqlalchemy.exc.SQLAlchemyError:
        flash('Unable to retrieve user favourites.')
    return redirect(url_for('base_bp.home'))


@like_bp.route('/classics')
def classics():
    try:
        classics = Classics.query.filter().all()
        classic_lookup = {}
        for c in classics:
            classic_lookup[c.transcript_id] = c.description
        transcripts = db.session.query(Transcript, Classics, Episode, Show).filter(
            Transcript.episode == Episode.id,
            Episode.show == Show.id,
            Transcript.id.in_(classic_lookup.keys()),
            Classics.transcript_id == Transcript.id).all()
        return render_template('like/classics.html', matches=transcripts)
    except sqlalchemy.exc.SQLAlchemyError:
        flash('Unable to retrieve user favourites.')
    return redirect(url_for('base_bp.home'))
