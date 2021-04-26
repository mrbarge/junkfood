from flask_login import UserMixin
from sqlalchemy import func, desc, Table, Column, ForeignKey, Integer
from sqlalchemy.sql.expression import func as sqlfunc
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
    number = db.Column(db.String(64))
    date = db.Column(db.Date)
    homepage = db.Column(db.Unicode(255))
    media = db.Column(db.Unicode(255))
    podcast = db.Column(db.Unicode(16))
    premium = db.Column(db.Boolean)
    archive = db.Column(db.Boolean)


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


def get_transcripts(episode_id):
    '''
    Retrieve a transcript for the given episode
    :return: Transcript
    '''
    try:
        all_transcripts = Transcript.query.filter(Transcript.episode == episode_id).order_by(Transcript.index)
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()

    return all_transcripts


def get_stars(user_id, episode_id):
    '''
    Retrieve user-starred transcripts for the given episode
    :param user_id: ID of user
    :param episode_id: ID of episode
    :return:
    '''
    try:
        all_transcripts = Transcript.query.filter(Transcript.episode == episode_id).order_by(Transcript.index)
        transcript_ids = [x.id for x in all_transcripts]
        episode_stars = StarredTranscripts.query.filter(StarredTranscripts.user_id == user_id,
                                                        StarredTranscripts.transcript_id.in_(transcript_ids))
        results = [row.transcript_id for row in episode_stars]
        return results
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()
    return []


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


def search(query, page, items_per_page, limit):
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

    matches = match_query.order_by(Transcript.episode).order_by(Transcript.timecode_secs).limit(limit).from_self().paginate(page,
                                                                                                   items_per_page,
                                                                                                   False)
    return matches


def get_terms_for_episode(episode_id, limit):
    '''
    Retrieves all detected terms for an episode
    :return: Transcript
    '''
    try:
        all_terms = TermFrequency.query.join(Terms).add_columns(Terms.id, Terms.term, Terms.label).filter(
            TermFrequency.episode_id == episode_id).order_by(TermFrequency.freq.desc()).limit(limit)
        terms = []
        for term in all_terms:
            terms.append({
                'id': term[1],
                'term': term[2],
                'label': term[3],
                'freq': term[0].freq
            })
        return terms
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()
    return []


def get_episodes_for_term(term_id):
    '''
    Retrieves all detected terms for an episode
    :return: Transcript
    '''
    try:
        term = Terms.query.filter(Terms.id == term_id).first()
        all_episodes = TermFrequency.query.filter(TermFrequency.term_id == term_id).order_by(
            TermFrequency.freq.desc()).limit(20)
        terms = []
        for ep in all_episodes:
            terms.append({
                'episode_id': ep.episode_id,
                'freq': ep.freq,
            })
        return terms
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()
    return []


def top_terms(limit):
    '''
    Retrieves all detected terms for an episode
    :return: Transcript
    '''
    try:
        all_terms = TermFrequency.query.with_entities(TermFrequency.term_id,
                                                      func.count(TermFrequency.freq).label('freq')).group_by(
            TermFrequency.term_id).order_by(desc('freq')).limit(limit)
        terms = []
        for t in all_terms:
            term = Terms.query.filter(Terms.id == t[0]).first()
            terms.append(term)
        return terms
    except sqlalchemy.exc.SQLAlchemyError:
        raise Exception()
    return []


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


def like_transcript(user_id, transcript_id):
    try:
        user_star = StarredTranscripts(user_id=user_id, transcript_id=transcript_id)
        db.session.add(user_star)
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise Exception(e)

    return user_star


def unlike_transcript(user_id, transcript_id):
    try:
        StarredTranscripts.query.filter(StarredTranscripts.user_id == user_id,
                                        StarredTranscripts.transcript_id == transcript_id).delete()
        db.session.commit()
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise Exception(e)


def my_likes(user_id):
    try:
        likes = StarredTranscripts.query.filter(StarredTranscripts.user_id == user_id)
        like_transcripts = [x.transcript_id for x in likes]
        transcripts = Transcript.query.join(Episode).add_columns(Episode.date, Episode.id, Episode.media).filter(
            Transcript.id.in_(like_transcripts)).all()
        return transcripts
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise Exception(e)
    return []


def top_likes():
    try:
        top_likes = StarredTranscripts.query.with_entities(StarredTranscripts.transcript_id,
                                                           func.count(StarredTranscripts.transcript_id).label(
                                                               'count')).group_by(
            StarredTranscripts.transcript_id).order_by(desc('count')).limit(20).all()
        like_transcripts = [x.transcript_id for x in top_likes]
        transcripts = Transcript.query.join(Episode).add_columns(Episode.date, Episode.id, Episode.media).filter(
            Transcript.id.in_(like_transcripts)).all()
        return transcripts
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise Exception(e)
    return []


def classics():
    try:
        classics = Classics.query.filter().all()
        classic_lookup = {}
        for c in classics:
            classic_lookup[c.transcript_id] = c.description
        transcripts = Transcript.query.join(Episode).add_columns(Classics.description, Episode.date, Episode.id,
                                                                 Episode.media).filter(
            Transcript.id.in_(classic_lookup.keys()),
            Classics.transcript_id == Transcript.id).all()
        return transcripts
    except sqlalchemy.exc.SQLAlchemyError as e:
        raise Exception(e)
    return []
