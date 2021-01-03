from flask_login import UserMixin
from sqlalchemy import Index, distinct, func, desc
from sqlalchemy.orm import relationship
import sqlalchemy

from . import db
from sqlalchemy.dialects.postgresql import JSON


class Transcript(db.Model):
    __tablename__ = 'transcripts'

    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer)
    episode = db.Column(db.Integer)
    speaker = db.Column(db.String(15))
    timecode = db.Column(db.String(8))
    timecode_secs = db.Column(db.Integer)
    transcript = db.Column(db.Text)

    def __repr__(self):
        return '<Transcript {}>'.format(self.id)


class Movies(db.Model):
    __tablename__ = 'movies'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    imdb_id = db.Column(db.String(15))
    release_date = db.Column(db.String(10))


class TranscriptMovies(db.Model):
    __tablename__ = 'transcript_movies'

    transcript_id = db.Column(
        db.Integer,
        db.ForeignKey('transcripts.id'),
        primary_key=True
    )
    movie_id = db.Column(
        db.Integer,
        db.ForeignKey('movies.id'),
        primary_key=True
    )


def get_episodes():
    '''
    Retrieve all episodes.
    :return: List of episode numbers
    '''
    try:
        all_episodes = Transcript.query.distinct(Transcript.episode)
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()

    results = [episode.episode for episode in all_episodes]
    return results


def get_transcripts(episode):
    '''
    Retrieve a transcript for the given episode
    :return: Transcript
    '''
    try:
        all_transcripts = Transcript.query.filter(Transcript.episode == episode).order_by(Transcript.index)
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()

    return all_transcripts


def get_speakers():
    '''
    Retrieve all speakers
    :return: List of speaker tuples (value,presented name)
    '''
    try:
        all_speakers = Transcript.query.with_entities(Transcript.speaker,
                                                      func.count(Transcript.speaker).label('total')).filter(
            ~Transcript.speaker.startswith('Unknown')).group_by(
            Transcript.speaker).order_by(desc('total'))
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()

    speakers = []
    for speaker in all_speakers:
        speakers.append((speaker.speaker, speaker.speaker))
    return speakers


def search(transcript, episode, speaker):
    try:
        match_query = Transcript.query.filter(Transcript.transcript.contains(transcript))
        if episode:
            match_query = match_query.filter(Transcript.episode == episode)
        if speaker:
            match_query = match_query.filter(Transcript.speaker.match(speaker))

        matches = match_query.order_by(Transcript.episode).order_by(Transcript.timecode_secs).all()

    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()

    return matches
