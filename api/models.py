from sqlalchemy import Integer, String, Column, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import UUIDType, EmailType

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import sessionmaker, mapper
import uuid


engine = create_engine('postgresql+psycopg2://admin:123456@localhost/escape')

if not engine.dialect.has_table(engine, 'users_'):
    metadata = MetaData(engine)

    # Create table eye_colors_
    eye_color = Table('eye_colors_', metadata,
          Column('id', UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False),
          Column('title', String, nullable=False),
          Column('description', String, nullable=False),
          )

    # Create table countries_
    country = Table('countries_', metadata,
          Column('id', UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False),
          Column('title', String, nullable=False),
          Column('description', String, nullable=False),
          )

    # Create table users_
    user = Table('users_', metadata,
          Column('id', UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False),
          Column('user_name', String, nullable=True),
          Column('user_surname', String, nullable=True),
          Column('user_middle_name', String, nullable=True),
          Column('user_date_of_birth', DateTime, nullable=True),
          Column('user_email', EmailType, nullable=False),
          Column('user_pass_hash', String, nullable=False),
          Column('access_token', String, nullable=False),
          Column('token_expired_date', DateTime, nullable=False),
          Column('eye_color_id', UUIDType(binary=False), ForeignKey('eye_colors_.id'), nullable=True),
          Column('country_id', UUIDType(binary=False), ForeignKey('countries_.id'), nullable=True),
          )

    # Create table albums_
    album = Table('albums_', metadata,
          Column('id', UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False),
          Column('user_id', UUIDType(binary=False), ForeignKey('users_.id'), nullable=False),
          Column('album_title', String, nullable=False),
          )

    # Create table photo_
    photo = Table('photo_', metadata,
          Column('id', UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False),
          Column('album_id', UUIDType(binary=False), ForeignKey('albums_.id'), nullable=False),
          Column('photo_caption', String, nullable=True),
          )
    metadata.create_all()


Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class EyeColor(Base):
    __tablename__ = 'eye_colors_'
    id = Column(UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    users = relationship('User', back_populates='eye_color')

    def __repr__(self):
        return "<EyeColor(title='%s')>" % (self.title,)


class Country(Base):
    __tablename__ = 'countries_'
    id = Column(UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)

    users = relationship('User', back_populates='country')

    def __repr__(self):
        return "<Country(title='%s')>" % (self.title,)


class User(Base):
    __tablename__ = 'users_'
    id = Column(UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False)
    albums = relationship("Album", backref="user")

    user_name = Column(String, nullable=True)
    user_surname = Column(String, nullable=True)
    user_middle_name = Column(String, nullable=True)
    user_date_of_birth = Column(DateTime, nullable=True)
    user_email = Column(EmailType, nullable=False)
    user_pass_hash = Column(String, nullable=False)
    access_token = Column(String, nullable=False)
    token_expired_date = Column(DateTime, nullable=False)

    eye_color_id = Column(UUIDType(binary=False), ForeignKey('eye_colors_.id'), nullable=True)
    eye_color = relationship('EyeColor', back_populates='users')
    country_id = Column(UUIDType(binary=False), ForeignKey('countries_.id'), nullable=True)
    country = relationship('Country', back_populates='users')

    UniqueConstraint('user_email')

    def __repr__(self):
        return "<User(user_name='%s', user_surname='%s', id='%s')>" % (self.user_name, self.user_surname, self.id)


class Album(Base):
    __tablename__ = 'albums_'
    id = Column(UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False)
    photo = relationship("Photo", backref="album")
    album_title = Column(String, nullable=False)

    user_id = Column(UUIDType(binary=False), ForeignKey(User.id), nullable=False)

    def __repr__(self):
        return "<Album(id='%s')>" % (self.id,)


class Photo(Base):
    __tablename__ = 'photo_'
    id = Column(UUIDType(binary=False), default=uuid.uuid4(), primary_key=True, nullable=False)
    photo_caption = Column(String, nullable=True)

    album_id = Column(Integer, ForeignKey(Album.id), nullable=False)

    def __repr__(self):
        return "<Photo(id='%s')>" % (self.id,)
