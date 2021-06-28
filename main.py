from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

API_KEY = 'b4860c2f4e1e9c2c58e8f16429c5e004'
SEARCH_MOVIE_URL = 'https://api.themoviedb.org/3/search/movie'
MOVIE_INFO_URL = 'https://api.themoviedb.org/3/movie/'
MOVIE_URL_IMG = 'https://image.tmdb.org/t/p/w500'


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)
db.create_all()

class RateMovieForm(FlaskForm):
    rating = FloatField('Rate the movie e.g. 7.5', validators=[DataRequired()])
    review = StringField('Your review', validators=[DataRequired()])
    submit = SubmitField('Done')

class AddAMovie(FlaskForm):
    title = StringField('Movie title', validators=[DataRequired()])
    submit = SubmitField('Add movie')

@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route("/edit", methods=["GET", "POST"])
def rate_movie():
    form = RateMovieForm()
    movie_id = request.args.get('id')
    movie = Movie.query.get(movie_id)
    if form.validate_on_submit():
        movie.rating = float(form.rating.data)
        movie.review = form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=form, movie=movie)

@app.route("/delete", methods=["GET", "POST"])
def delete_movie():
    movie_id = request.args.get('id')
    movie_to_delete = Movie.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["GET", "POST"])
def add_movie():
    form = AddAMovie()
    if form.validate_on_submit():
        movie_title = form.title.data
        response = requests.get(SEARCH_MOVIE_URL, params={'api_key': API_KEY, 'query': movie_title})
        data = response.json()['results']
        return render_template('select.html', options=data)
    return render_template('add.html', form=form)

@app.route("/find")
def find_movie():
    movie_api_id = request.args.get('id')
    if movie_api_id:
        movie_api_url = f'{MOVIE_INFO_URL}/{movie_api_id}'
        response = requests.get(movie_api_url, params={'api_key':API_KEY})
        data = response.json()
        new_movie = Movie(
            title=data['title'],
            img_url=f"{MOVIE_URL_IMG}{data['poster_path']}",
            year=data['release_date'].split('-')[0],
            description=data['overview']
        )
        db.session.add(new_movie)
        db.session.commit()
        return redirect(url_for('rate_movie', id=new_movie.id))

if __name__ == '__main__':
    app.run(debug=True)
