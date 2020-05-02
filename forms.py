from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField
from wtforms.validators import DataRequired, AnyOf, URL
from data import genres, states


class VenueForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[DataRequired(), AnyOf(states)],
        choices=states
    )
    address = StringField(
        'address',
        validators=[DataRequired()]
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link',
        validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired(), AnyOf(genres)],
        choices=genres
    )
    website = StringField(
        'website',
        validators=[URL()]
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[URL()]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description'
    )


class ArtistForm(Form):
    name = StringField(
        'name',
        validators=[DataRequired()]
    )
    city = StringField(
        'city',
        validators=[DataRequired()]
    )
    state = SelectField(
        'state',
        validators=[DataRequired(), AnyOf(states)],
        choices=states
    )
    phone = StringField(
        'phone'
    )
    image_link = StringField(
        'image_link',
        validators=[URL()]
    )
    website = StringField(
        'website',
        validators=[URL()]
    )
    facebook_link = StringField(
        'facebook_link',
        validators=[URL()]
    )
    genres = SelectMultipleField(
        'genres',
        validators=[DataRequired(), AnyOf(genres)],
        choices=genres
    )
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = StringField(
        'seeking_description'
    )


class ShowForm(Form):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired()],
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired()],
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default=datetime.today()
    )
