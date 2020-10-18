from flask_login import UserMixin
from sqlalchemy import Index, distinct

from . import db
from sqlalchemy.dialects.postgresql import JSON


class Transcript(db.Model):
    __tablename__ = 'transcripts'

    id = db.Column(db.Integer)
    index = db.Column(db.Integer, primary_key=True)
    episode = db.Column(db.Integer, primary_key=True)
    speaker = db.Column(db.String(15))
    timecode = db.Column(db.String(8))
    timecode_secs = db.Column(db.Integer)
    transcript = db.Column(db.Text)

    def __repr__(self):
        return '<Transcript {}>'.format(self.id)


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

