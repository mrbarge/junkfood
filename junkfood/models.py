from flask_login import UserMixin
from sqlalchemy import Index, distinct, func, desc, Table, Column, ForeignKey, Integer
from sqlalchemy.sql.expression import func as sqlfunc
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import random

from . import db, searchquery
from junkfood import login_manager
from sqlalchemy.dialects.postgresql import JSON
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


Base = declarative_base()
role_association_table = Table('user_roles', Base.metadata,
                               )


class RoleAssociation(db.Model):
    __tablename__ = 'user_roles'
    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Unicode(16), nullable=False, unique=True)

    def __repr__(self):
        return '<Role {}>'.format(self.role)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(40), unique=True, nullable=False)
    password = db.Column(db.String(200), primary_key=False, unique=False, nullable=False)
    roles = relationship('RoleAssociation')

    def set_password(self, password):
        if not password:
            raise ValueError('Password cannot be empty')
        self.password = generate_password_hash(password, method='sha256')

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return '<User {}>'.format(self.email)


class Episode(db.Model):
    __tablename__ = 'episodes'

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date)
    homepage = db.Column(db.String(255))
    media = db.Column(db.String(255))
    podcast = db.Column(db.String(16))
    premium = db.Column(db.Boolean)
    archive = db.Column(db.Boolean)


class Transcript(db.Model):
    __tablename__ = 'transcripts'

    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer)
    episode = db.Column(db.Integer,
                        db.ForeignKey('episodes.id'),
                        )
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


def get_random_episode():
    '''
    Retrieve episode with id.
    :return: List of episode numbers
    '''
    try:
        episode = Episode.query.filter().order_by(sqlfunc.random()).first()
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()

    return episode


def get_episode(id):
    '''
    Retrieve episode with id.
    :return: List of episode numbers
    '''
    try:
        episode = Episode.query.filter(Episode.id == id).first()
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()

    return episode


def get_all_episode_ids(has_transcript=True):
    '''
    Retrieve all episodes.
    :return: List of episode numbers
    '''
    try:
        if has_transcript:
            rows = Transcript.query.distinct(Transcript.episode)
            results = [transcript.episode for transcript in rows]
        else:
            rows = Episode.query.distinct(Episode.id)
            results = [episode.id for episode in rows]

        return results

    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()


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


def search(query, page, items_per_page):
    '''
    Retrieve episodes matching query
    :param query:
    :return:
    '''
    parsed_query = searchquery.parse_query(query)

    match_query = Transcript.query.join(Episode).add_columns(Episode.date, Episode.id, Episode.media).filter()
    if searchquery.PHRASE_KEY in parsed_query:
        for phrase in parsed_query[searchquery.PHRASE_KEY]:
            match_query = match_query.filter(Transcript.transcript.ilike(f'%{phrase}%'))
    if searchquery.EPISODE_KEY in parsed_query:
        iv = int(parsed_query[searchquery.EPISODE_KEY][0])
        match_query = match_query.filter(Transcript.episode == iv)
    if searchquery.SPEAKER_KEY in parsed_query:
        match_query = match_query.filter(Transcript.speaker.match(parsed_query[searchquery.SPEAKER_KEY][0]))
    if searchquery.SINCE_KEY in parsed_query:
        match_query = match_query.filter(Episode.date >= parsed_query[searchquery.SINCE_KEY][0])
    if searchquery.UNTIL_KEY in parsed_query:
        match_query = match_query.filter(Episode.date <= parsed_query[searchquery.UNTIL_KEY][0])

    matches = match_query.order_by(Transcript.episode).order_by(Transcript.timecode_secs).paginate(page, items_per_page,
                                                                                                   False)
    return matches


def searchFields(transcript, episode, speaker):
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
