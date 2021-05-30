from flask_login import UserMixin
from sqlalchemy import func, desc, Table, Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy

from . import db, searchquery
from junkfood import login_manager
from werkzeug.security import generate_password_hash, check_password_hash


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)
    return None


Base = declarative_base()
role_association_table = Table('user_roles', Base.metadata)


class RoleAssociation(db.Model):
    __tablename__ = 'user_roles'
    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    role_id = Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)


class StarredTranscripts(db.Model):
    __tablename__ = 'user_starred'
    user_id = Column('user_id', Integer, ForeignKey('users.id'), primary_key=True)
    transcript_id = Column('transcript_id', Integer, ForeignKey('transcripts.id'), primary_key=True)


class Classics(db.Model):
    __tablename__ = 'classics'
    transcript_id = Column('transcript_id', Integer, ForeignKey('transcripts.id'), primary_key=True)
    description = Column('description', db.Text)


class Terms(db.Model):
    __tablename__ = 'terms'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term = Column('term', db.Text)
    label = Column('label', db.String(20))


class TermFrequency(db.Model):
    __tablename__ = 'termfreq'
    term_id = Column('term_id', Integer, ForeignKey('terms.id'), primary_key=True, autoincrement=False)
    episode_id = Column('episode_id', Integer, ForeignKey('episodes.id'), primary_key=True, autoincrement=False)
    freq = Column('freq', db.Integer)


class Show(db.Model):
    __tablename__ = 'show'
    id = Column(db.Integer, primary_key=True, autoincrement=True)
    title = Column('title', db.String(20))
    logo = Column('logo', db.String(50))


class Role(db.Model):
    __tablename__ = 'roles'

    ADMINISTRATOR = 'Administrator'
    MODERATOR = 'Moderator'
    PREMIUM = 'Premium'

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Unicode(16), nullable=False, unique=True)

    def __repr__(self):
        return '<Role {}>'.format(self.role)


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.Unicode(40), unique=True, nullable=False)
    password = db.Column(db.String(200), primary_key=False, unique=False, nullable=False)
    email_confirmed = db.Column(db.Boolean, default=False)
    roles = relationship('RoleAssociation')
    starred = relationship('StarredTranscripts')

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
    episode = db.Column(db.String(64))
    date = db.Column(db.Date)
    title = db.Column(db.Unicode(255))
    homepage = db.Column(db.Unicode(255))
    media = db.Column(db.Unicode(255))
    premium = db.Column(db.Boolean)
    archive = db.Column(db.Boolean)
    show = db.Column(db.Integer, db.ForeignKey('show.id'))


class Transcript(db.Model):
    __tablename__ = 'transcripts'

    id = db.Column(db.Integer, primary_key=True)
    index = db.Column(db.Integer)
    episode = db.Column(db.Integer,
                        db.ForeignKey('episodes.id'),
                        )
    speaker = db.Column(db.Unicode(15))
    timecode = db.Column(db.String(8))
    timecode_secs = db.Column(db.Integer)
    transcript = db.Column(db.Text)

    def __repr__(self):
        return '<Transcript {}>'.format(self.id)


def search(query, page, items_per_page, limit):
    '''
    Retrieve episodes matching query
    :param query:
    :return:
    '''
    parsed_query = searchquery.parse_query(query)

    match_query = db.session.query(Transcript, Episode, Show).filter(Transcript.episode == Episode.id,
                                                                     Episode.show == Show.id)
    if searchquery.PHRASE_KEY in parsed_query:
        for phrase in parsed_query[searchquery.PHRASE_KEY]:
            match_query = match_query.filter(Transcript.transcript.ilike(f'%{phrase}%'))
    if searchquery.EPISODE_KEY in parsed_query:
        iv = parsed_query[searchquery.EPISODE_KEY][0]
        match_query = match_query.filter(Episode.episode == iv)
    if searchquery.SPEAKER_KEY in parsed_query:
        match_query = match_query.filter(
            func.lower(Transcript.speaker) == func.lower(parsed_query[searchquery.SPEAKER_KEY][0]))
    if searchquery.SINCE_KEY in parsed_query:
        match_query = match_query.filter(Episode.date >= parsed_query[searchquery.SINCE_KEY][0])
    if searchquery.SHOW_KEY in parsed_query:
        match_query = match_query.filter(func.lower(Show.title) == func.lower(parsed_query[searchquery.SHOW_KEY][0]))
    if searchquery.UNTIL_KEY in parsed_query:
        match_query = match_query.filter(Episode.date <= parsed_query[searchquery.UNTIL_KEY][0])

    matches = match_query.order_by(Transcript.episode).order_by(Transcript.timecode_secs).limit(
        limit).from_self().paginate(page,
                                    items_per_page,
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
