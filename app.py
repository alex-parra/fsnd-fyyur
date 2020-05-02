#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(500))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean())
    seeking_description = db.Column(db.Text())

    @property
    def genres_list(self):
        return json.loads(self.genres)

    @property
    def upcoming_shows(self):
        return [s for s in self.shows if s.start_time > datetime.today()]

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)

    @property
    def past_shows(self):
        return [s for s in self.shows if s.start_time <= datetime.today()]

    @property
    def past_shows_count(self):
        return len(self.past_shows)


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(500))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean())
    seeking_description = db.Column(db.Text())

    @property
    def genres_list(self):
        return json.loads(self.genres)

    @property
    def upcoming_shows(self):
        return [s for s in self.shows if s.start_time > datetime.today()]

    @property
    def upcoming_shows_count(self):
        return len(self.upcoming_shows)

    @property
    def past_shows(self):
        return [s for s in self.shows if s.start_time <= datetime.today()]

    @property
    def past_shows_count(self):
        return len(self.past_shows)


class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime())

    venue = db.relationship('Venue', backref=db.backref('shows', lazy=True))
    artist = db.relationship('Artist', backref=db.backref('shows', lazy=True))

    @property
    def venue_name(self):
        return self.venue.name

    @property
    def venue_image_link(self):
        return self.venue.image_link

    @property
    def artist_name(self):
        return self.artist.name

    @property
    def artist_image_link(self):
        return self.artist.image_link

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = value
    if type(date) is str:
        date = dateutil.parser.parse(date)

    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/', methods=['GET'])
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues', methods=['GET'])
def venues():
    venues = Venue.query.all()
    areas = {(v.city, v.state) for v in venues}
    data = [{
        'city': city,
        'state': state,
        'venues': [venue for venue in venues if venue.city == city and venue.state == state]
    } for city, state in areas]
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['GET'])
def search_venues():
    search_term = request.args.get('q', '')
    search_term_filter = Venue.name.ilike("%{}%".format(search_term))
    matches = Venue.query.filter(search_term_filter).all()
    response = {"count": len(matches), "data": matches}
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        return abort(404)
    return render_template('pages/show_venue.html', venue=venue)


@app.route('/venues/create', methods=['GET'])
def create_venue():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    newVenue = Venue()
    form = VenueForm(request.form)
    form.populate_obj(newVenue)
    newVenue.genres = json.dumps(request.form.getlist('genres'))
    try:
        db.session.add(newVenue)
        db.session.commit()
        data = Venue.query.filter(Venue.name == newVenue.name).first()
        flash(newVenue.name + ' was successfully listed!')
    except:
        flash('Failed: ' + newVenue.name + ' could not be created.')
    return redirect(url_for('venues'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        return abort(404)
    form = VenueForm(obj=venue)
    form.genres.data = venue.genres_list
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        return abort(404)
    form = VenueForm(request.form, obj=venue)
    form.genres.data = venue.genres_list
    form.populate_obj(venue)
    venue.genres = json.dumps(request.form.getlist('genres'))
    try:
        db.session.add(venue)
        db.session.commit()
        return redirect(url_for('show_venue', venue_id=venue_id))
    except:
        flash('Failed to save changes')
        return redirect(url_for('edit_venue', venue_id=venue_id))


@app.route('/venues/<int:venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        return abort(404)
    db.session.delete(venue)
    db.session.commit()
    return 'OK'


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists', methods=['GET'])
def artists():
    data = Artist.query.order_by(Artist.id).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['GET'])
def search_artists():
    search_term = request.args.get('q', '')
    search_term_filter = Artist.name.ilike("%{}%".format(search_term))
    matches = Artist.query.filter(search_term_filter).all()
    response = {"count": len(matches), "data": matches}
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        return abort(404)
    return render_template('pages/show_artist.html', artist=artist)


@app.route('/artists/create', methods=['GET'])
def create_artist():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    newArtist = Artist()
    form = ArtistForm(request.form)
    form.populate_obj(newArtist)
    newArtist.genres = json.dumps(request.form.getlist('genres'))
    try:
        db.session.add(newArtist)
        db.session.commit()
        flash(newArtist.name + ' was successfully listed!')
    except:
        flash('Failed: ' + newArtist.name + ' could not be created.')
    return redirect(url_for('artists'))


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        return abort(404)
    form = ArtistForm(obj=artist)
    form.genres.data = artist.genres_list
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        return abort(404)
    form = ArtistForm(request.form, obj=artist)
    form.genres.data = artist.genres_list
    form.populate_obj(artist)
    artist.genres = json.dumps(request.form.getlist('genres'))
    try:
        db.session.add(artist)
        db.session.commit()
        return redirect(url_for('show_artist', artist_id=artist_id))
    except:
        flash('Failed to save changes')
        return redirect(url_for('edit_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows', methods=['GET'])
def shows():
    shows = Show.query.all()
    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/search', methods=['GET'])
def search_shows():
    search_term = request.args.get('q', '')
    matches = Show.query.join(Show.artist).filter(or_(
        Artist.name.ilike("%{}%".format(search_term)),
        Venue.name.ilike("%{}%".format(search_term))
    )).all()
    response = {"count": len(matches), "data": matches}
    return render_template('pages/search_shows.html', results=response, search_term=search_term)


@app.route('/shows/create', methods=['GET'])
def create_show():
    form = ShowForm()
    artists = Artist.query.all()
    venues = Venue.query.all()
    return render_template('forms/new_show.html', form=form, artists=artists, venues=venues)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    newShow = Show()
    form = ShowForm()
    form.populate_obj(newShow)
    try:
        db.session.add(newShow)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        flash('Failed: Show could not be created.')

    return redirect(url_for('shows'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
