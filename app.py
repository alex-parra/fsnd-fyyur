#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
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
    matches = Venue.query.filter(
        Venue.name.ilike("%{}%".format(search_term))).all()

    response = {"count": len(matches), "data": matches}
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>', methods=['GET'])
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    return render_template('pages/show_venue.html', venue=venue)


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    newVenue = Venue()
    newVenue.name = request.form.get('name')
    newVenue.address = request.form.get('address')
    newVenue.city = request.form.get('city')
    newVenue.state = request.form.get('state')
    newVenue.phone = request.form.get('phone')
    newVenue.genres = json.dumps(request.form.getlist('genres'))
    newVenue.facebook_link = request.form.get('facebook_link')
    newVenue.seeking_talent = request.form.get(
        'seeking_talent', default=False, type=bool)
    newVenue.seeking_description = request.form.get('seeking_description')
    db.session.add(newVenue)

    try:
        db.session.commit()
        data = Venue.query.filter(Venue.name == newVenue.name).first()
        flash('Venue ' + data.name + ' was successfully listed!')
    except:
        flash('An error occurred. Venue ' +
              newVenue.name + ' could not be created.')

    return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    form.genres.data = venue.genres_list
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form, obj=venue)
    form.genres.data = venue.genres_list
    # TODO: Validation
    form.populate_obj(venue)
    venue.genres = json.dumps(request.form.getlist('genres'))
    db.session.add(venue)
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))


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
    matches = Artist.query.filter(
        Artist.name.ilike("%{}%".format(search_term))).all()

    response = {"count": len(matches), "data": matches}
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>', methods=['GET'])
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    return render_template('pages/show_artist.html', artist=artist)


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Rock n Roll"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    return redirect(url_for('show_artist', artist_id=artist_id))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows', methods=['GET'])
def shows():
    shows = Show.query.all()
    return render_template('pages/shows.html', shows=shows)


@app.route('/shows/create', methods=['GET'])
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    # on successful db insert, flash success
    flash('Show was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


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
