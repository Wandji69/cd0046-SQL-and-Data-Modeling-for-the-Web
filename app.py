#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from __future__ import generator_stop
from curses import meta
from datetime import date
from email.policy import default
from itertools import count
import json
from lib2to3.pgen2.tokenize import generate_tokens
from os import abort, stat
import sys
from unicodedata import name
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# DONE: connect to a local postgresql database
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.String(255), nullable=False)
    website_link = db.Column(db.String(255))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(255))
    show = db.relationship('Show', backref='venue', lazy=True)

    def __repr__(self):
        return f'<Venue: ID: {self.id}, name: {self.name}, genres: {self.genres}, city: {self.city}, state: {self.state}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # DONE: implement any missing fields, as a database migration using Flask-Migrate
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String())
    show = db.relationship('Show', backref='artist', lazy=True)

    def __repr__(self):
        return f'<Artist: ID: {self.id}, name: {self.name}>'

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.String())
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artist.id'), nullable=False)

    def __repr__(self):
        return f'<Show: ID: {self.id}, Venue: {self.venue_id}, Artist: {self.artist_id}>'

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    data = Venue.query.all()
    mydata = set()
    for d in data:
        mydata.add((
            d.state,
            d.city
        ))
    venue_data = []

    for state, city in mydata:
        venue_data.append({
            "state": state,
            "city": city,
            "venues": [{
                "id": venue.id,
                "name": venue.name
            } for venue in data if venue.city == city and venue.state == state]
        })
    # DONE: replace with real venues data.
    # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data1 = [{
        "city": "San Francisco",
        "state": "CA",
        "venues": [{
                "id": 1,
                "name": "The Musical Hop",
                "num_upcoming_shows": 0,
        }, {
            "id": 3,
            "name": "Park Square Live Music & Coffee",
            "num_upcoming_shows": 1,
        }]
    }, {
        "city": "New York",
        "state": "NY",
        "venues": [{
                "id": 2,
                "name": "The Dueling Pianos Bar",
                "num_upcoming_shows": 0,
        }]
    }]
    return render_template('pages/venues.html', areas=venue_data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    key_word = request.form.get('search_term', '')
    response = Venue.query.filter(Venue.name.ilike(f'%{key_word}%')).all()
    data = []
    for venue in response:
        data.append({
            "id": venue.id,
            "name": venue.name
        })
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response_data = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response_data, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id
    data = Venue.query.get_or_404(venue_id)
    past_shows_data = data.show
    past_shows_data = [
        show for show in past_shows_data if
        (datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") < datetime.now())
    ]
    # Show.query.filter(Show.venue_id == venue_id).filter(
    #     datetime.strptime(str(Show.start_time), "%Y-%m-%d %H:%M:%S") < datetime.now()).all()
    upcoming_shows_data = data.show
    upcoming_shows_data = [
        show for show in past_shows_data if
        (datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") > datetime.now())
    ]

    upcoming_shows = []
    for up in upcoming_shows_data:
        artist_data = Artist.query.get(up.artist_id)
        upcoming_shows.append({
            "artist_id": artist_data.id,
            "artist_name": artist_data.name,
            "artist_image_link": artist_data.image_link,
            "start_time": up.start_time
        })

    past_shows = []
    for d in past_shows_data:
        artist_data = Artist.query.get(d.artist_id)
        past_shows.append({
            "artist_id": artist_data.id,
            "artist_name": artist_data.name,
            "artist_image_link": artist_data.image_link,
            "start_time": d.start_time
        })
    data1 = {
        "id": data.id,
        "name": data.name,
        "genres": [data.genres],
        "address": data.address,
        "city": data.city,
        "state": data.state,
        "phone": data.state,
        "website": data.image_link,
        "facebook_link": data.facebook_link,
        "seeking_talent": data.seeking_talent,
        "seeking_description": data.seeking_description,
        "image_link": data.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    data2 = {
        "id": 2,
        "name": "The Dueling Pianos Bar",
        "genres": ["Classical", "R&B", "Hip-Hop"],
        "address": "335 Delancey Street",
        "city": "New York",
        "state": "NY",
        "phone": "914-003-1132",
        "website": "https://www.theduelingpianos.com",
        "facebook_link": "https://www.facebook.com/theduelingpianos",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
        "past_shows": [],
        "upcoming_shows": [],
        "past_shows_count": 0,
        "upcoming_shows_count": 0,
    }
    data3 = {
        "id": 3,
        "name": "Park Square Live Music & Coffee",
        "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
        "address": "34 Whiskey Moore Ave",
        "city": "San Francisco",
        "state": "CA",
        "phone": "415-000-1234",
        "website": "https://www.parksquarelivemusicandcoffee.com",
        "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
        "seeking_talent": False,
        "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
        "past_shows": [{
                "artist_id": 5,
                "artist_name": "Matt Quevedo",
                "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
                "start_time": "2019-06-15T23:00:00.000Z"
        }],
        "upcoming_shows": [{
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z"
        }, {
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z"
        }],
        "past_shows_count": 1,
        "upcoming_shows_count": 1,
    }
    data_show = list(filter(lambda d: d['id'] ==
                            venue_id, [data1]))[0]
    return render_template('pages/show_venue.html', venue=data_show)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # insert form data as a new Venue record in the db, instead
    # modify data to be the data object returned from db insertion
    form = VenueForm()
    try:
        new = request.form
        name = new.get('name')
        city = new.get('city')
        state = new.get('state')
        address = new.get('name')
        phone = new.get('phone')
        genres = ",".join(new.getlist('genres'))
        facebook_link = new.get('facebook_link')
        image_link = new.get('image_link')
        website_link = new.get('website_link')
        seeking_talent = True if new.get('seeking_talent', '') else False
        seeking_description = new.get('seeking_description')

        new_venue = Venue(
            name=name,
            city=city,
            state=state,
            address=address,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website_link=website_link,
            seeking_talent=seeking_talent,
            seeking_description=seeking_description
        )
        db.session.add(new_venue)
        db.session.commit()
        # on successful db insert, flash success
        flash('Venue ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as err:
        db.session.rollback()
        print(err)
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()

    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html', form=form)


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        venue = Venue.query.filter_by(id=venue_id)
        db.session.delete(venue)
        db.session.commit()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
        abort(500)
    else:
        return None

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    artist = Artist.query.order_by('id').all()
    return render_template('pages/artists.html', artists=artist)

    data = [{
        "id": 4,
        "name": "Guns N Petals",
    }, {
        "id": 5,
        "name": "Matt Quevedo",
    }, {
        "id": 6,
        "name": "The Wild Sax Band",
    }]


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    key_word = request.form.get('search_term')
    response = Artist.query.filter(Artist.name.ilike(f'%{key_word}%')).all()
    data = []
    for artist in response:
        data.append({
            "id": artist.id,
            "name": artist.name
        })
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response_data = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response_data, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # Done: replace with real artist data from the artist table, using artist_id
    data = Artist.query.get_or_404(artist_id)
    past_shows_data = data.show
    past_shows_data = [
        show for show in past_shows_data if
        (datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") < datetime.now())
    ]
    # Show.query.filter(Show.venue_id == venue_id).filter(
    #     datetime.strptime(str(Show.start_time), "%Y-%m-%d %H:%M:%S") < datetime.now()).all()
    upcoming_shows_data = data.show
    upcoming_shows_data = [
        show for show in past_shows_data if
        (datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") > datetime.now())
    ]

    upcoming_shows = []
    for up in upcoming_shows_data:
        venue_data = Venue.query.get(up.venue_id)
        upcoming_shows.append({
            "venue_id": venue_data.id,
            "venue_name": venue_data.name,
            "venue_image_link": venue_data.image_link,
            "start_time": up.start_time
        })

    past_shows = []
    for d in past_shows_data:
        venue_data = Venue.query.get(d.venue_id)
        past_shows.append({
            "venue_id": venue_data.id,
            "venue_name": venue_data.name,
            "venue_image_link": venue_data.image_link,
            "start_time": d.start_time
        })
    data1 = {
        "id": data.id,
        "name": data.name,
        "genres": [data.genres],
        "city": data.city,
        "state": data.state,
        "phone": data.state,
        "website": data.image_link,
        "facebook_link": data.facebook_link,
        "seeking_venue": data.seeking_venue,
        "seeking_description": data.seeking_description,
        "image_link": data.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data1]))[0]
    return render_template('pages/show_artist.html', artist=data)


# data1 = {
#         "id": 4,
#         "name": "Guns N Petals",
#         "genres": ["Rock n Roll"],
#         "city": "San Francisco",
#         "state": "CA",
#         "phone": "326-123-5000",
#         "website": "https://www.gunsnpetalsband.com",
#         "facebook_link": "https://www.facebook.com/GunsNPetals",
#         "seeking_venue": True,
#         "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
#         "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
#         "past_shows": [{
#                 "venue_id": 1,
#                 "venue_name": "The Musical Hop",
#                 "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
#                 "start_time": "2019-05-21T21:30:00.000Z"
#         }],
#         "upcoming_shows": [],
#         "past_shows_count": 1,
#         "upcoming_shows_count": 0,
#     }
# data2 = {
#         "id": 5,
#         "name": "Matt Quevedo",
#         "genres": ["Jazz"],
#         "city": "New York",
#         "state": "NY",
#         "phone": "300-400-5000",
#         "facebook_link": "https://www.facebook.com/mattquevedo923251523",
#         "seeking_venue": False,
#         "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
#         "past_shows": [{
#                 "venue_id": 3,
#                 "venue_name": "Park Square Live Music & Coffee",
#                 "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#                 "start_time": "2019-06-15T23:00:00.000Z"
#         }],
#         "upcoming_shows": [],
#         "past_shows_count": 1,
#         "upcoming_shows_count": 0,
#     }
# data3 = {
#         "id": 6,
#         "name": "The Wild Sax Band",
#         "genres": ["Jazz", "Classical"],
#         "city": "San Francisco",
#         "state": "CA",
#         "phone": "432-325-5432",
#         "seeking_venue": False,
#         "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
#         "past_shows": [],
#         "upcoming_shows": [{
#                 "venue_id": 3,
#                 "venue_name": "Park Square Live Music & Coffee",
#                 "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#                 "start_time": "2035-04-01T20:00:00.000Z"
#         }, {
#             "venue_id": 3,
#             "venue_name": "Park Square Live Music & Coffee",
#             "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#             "start_time": "2035-04-08T20:00:00.000Z"
#         }, {
#             "venue_id": 3,
#             "venue_name": "Park Square Live Music & Coffee",
#             "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
#             "start_time": "2035-04-15T20:00:00.000Z"
#         }],
#         "past_shows_count": 0,
#         "upcoming_shows_count": 3,
#     }


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist1 = {
        "id": 4,
        "name": "Guns N Petals",
        "genres": ["Guns N Petals"],
        "city": "San Francisco",
        "state": "CA",
        "phone": "326-123-5000",
        "website": "https://www.gunsnpetalsband.com",
        "facebook_link": "https://www.facebook.com/GunsNPetals",
        "seeking_venue": True,
        "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
        "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
    }
    # DONE: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.get(artist_id)
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website_link
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link

    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    try:
        artist = Artist.query.get(artist_id)
        new_artist = request.form
        artist.name = new_artist.get('name')
        artist.city = new_artist.get('city')
        artist.state = new_artist.get('state')
        artist.phone = new_artist.get('phone')
        artist.genres = ",".join(new_artist.getlist('genres'))
        artist.facebook_link = new_artist.get('facebook_link')
        artist.image_link = new_artist.get('image_link')
        artist.website_link = new_artist.get('website_link')
        artist.seeking_venue = True if new_artist.get(
            'seeking_venue', '') else False
        artist.seeking_description = new_artist.get('seeking_description')
        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' was successfully updated!')
    except Exception as error:
        db.session.roolback()
        print(error)
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be update.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue1 = {
        "id": 1,
        "name": "The Musical Hop",
        "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
        "address": "1015 Folsom Street",
        "city": "San Francisco",
        "state": "CA",
        "phone": "123-123-1234",
        "website": "https://www.themusicalhop.com",
        "facebook_link": "https://www.facebook.com/TheMusicalHop",
        "seeking_talent": True,
        "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
        "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
    }
    # DONE: populate form with values from venue with ID <venue_id>
    venue = Venue.query.get(venue_id)
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.website_link.data = venue.website_link
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    try:
        venue = Venue.query.get(venue_id)
        new = request.form
        venue.name = new.get('name')
        venue.city = new.get('city')
        venue.state = new.get('state')
        venue.address = new.get('name')
        venue.phone = new.get('phone')
        venue.genres = ",".join(new.getlist('genres'))
        venue.facebook_link = new.get('facebook_link')
        venue.image_link = new.get('image_link')
        venue.website_link = new.get('website_link')
        venue.seeking_talent = True if new.get('seeking_talent', '') else False
        venue.seeking_description = new.get('seeking_description')
        db.session.commit()
        flash('Venue ' + request.form['name'] +
              ' was successfully updated!')
    except Exception as error:
        db.session.rollback()
        print(error)
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    form = ArtistForm()
    try:
        new_artist = request.form
        name = new_artist.get('name')
        city = new_artist.get('city')
        state = new_artist.get('state')
        phone = new_artist.get('phone')
        genres = ",".join(new_artist.getlist('genres'))
        facebook_link = new_artist.get('facebook_link')
        image_link = new_artist.get('image_link')
        website_link = new_artist.get('website_link')
        seeking_venue = True if new_artist.get('seeking_venue', '') else False
        seeking_description = new_artist.get('seeking_description')

        new = Artist(
            name=name,
            city=city,
            state=state,
            phone=phone,
            genres=genres,
            image_link=image_link,
            facebook_link=facebook_link,
            website_link=website_link,
            seeking_venue=seeking_venue,
            seeking_description=seeking_description
        )
        db.session.add(new)
        db.session.commit()
        flash('Artist ' + request.form['name'] +
              ' was successfully listed!')
    except Exception as err:
        db.session.rollback()
        print(err)
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.')
    finally:
        db.session.close()
    # on successful db insert, flash success
    # DONE: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html', form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.
    data = Show.query.all()
    my_show = []
    for show in data:
        venue = Venue.query.get(show.venue_id)
        # print(show.start_time)
        artist = Artist.query.get(show.artist_id)
        my_show.append({
            "venue_id": venue.id,
            "venue_name": venue.name,
            "artist_id": artist.id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": show.start_time
        })

    data1 = [{
        "venue_id": 1,
        "venue_name": "The Musical Hop",
        "artist_id": 4,
        "artist_name": "Guns N Petals",
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": "2019-05-21T21:30:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 5,
        "artist_name": "Matt Quevedo",
        "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
        "start_time": "2019-06-15T23:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-01T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-08T20:00:00.000Z"
    }, {
        "venue_id": 3,
        "venue_name": "Park Square Live Music & Coffee",
        "artist_id": 6,
        "artist_name": "The Wild Sax Band",
        "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
        "start_time": "2035-04-15T20:00:00.000Z"
    }]
    return render_template('pages/shows.html', shows=my_show)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # Done: insert form data as a new Show record in the db, instead
    form = ShowForm()
    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        new_show = Show(
            artist_id=artist_id,
            venue_id=venue_id,
            start_time=start_time
        )
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    except Exception as err:
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
        print(err)
        # Done: on unsuccessful db insert, flash an error instead.
    finally:
        db.session.close()
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
