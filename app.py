# -*- coding: utf-8 -*-

import os, datetime
import re
from unidecode import unidecode

from flask import Flask, request, render_template, redirect, abort

# import all of mongoengine
# from mongoengine import *
from flask.ext.mongoengine import mongoengine

# import data models
import models

app = Flask(__name__)   # create our flask app
app.config['CSRF_ENABLED'] = False

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
mongoengine.connect('mydata', host=os.environ.get('MONGOLAB_URI'))
app.logger.debug("Connecting to MongoLabs")


# Create the lists that match the name of the ListField in the models.py
bookType = ['Paperback','Hardcover','PDF','Kindle']
genre = ['Fiction', 'Programming', 'Physical Computing', 'ITP Essentials', 'Design', 'Art']
itpStatus = ['Current Student', 'ITP Alumni', 'Faculty', 'Resident', 'ITP Adjunct']


# --------- Routes ----------


# this is our main page
@app.route("/")
def index():
	# render the template, retrieve 'books' from the database
	return render_template("main.html", books=models.Book.objects())


@app.route("/submit", methods=['GET','POST'])
def submit():

	app.logger.debug(request.form.getlist('bookType'))
	app.logger.debug(request.form.getlist('genre'))
	app.logger.debug(request.form.getlist('itpStatus'))

	# get new books items form from models.py
	book_form = models.BookForm(request.form)
	
	if request.method == "POST" and book_form.validate():
	
		# get form data - create new book
		book = models.Book()
		
		book.title = request.form.get('title','no title')
		book.slug = slugify(book.title)
		book.author = request.form.get('author','anonymous')
		book.bookType = request.form.getlist('bookType')
		book.genre = request.form.getlist('genre')
		book.description = request.form.get('description','')
		
		book.owner = request.form.get('owner')
		book.email = request.form.get('email')
		book.itpStatus = request.form.getlist('itpStatus')
		
		book.save()

		return redirect('/books/%s' % book.slug)

	else:

		# for form management, checkboxes are weird (in wtforms)
		# prepare checklist items for form
		# you'll need to take the form checkboxes submitted
		# and book_form.bookType, book_form.genre and book_form.itpStatus list needs to be populated.
		if request.form.getlist('bookType'):
			for b in request.form.getlist('bookType'):
				idea_form.bookType.append_entry(b)

		if request.form.getlist('genre'):
			for g in request.form.getlist('genre'):
				idea_form.genre.append_entry(g)

		if request.form.getlist('itpStatus'):
			for i in request.form.getlist('itpStatus'):
				idea_form.itpStatus.append_entry(i)

		# render the template
		templateData = {
			'books' : models.Book.objects(),
			'bookType' : bookType,
			'genre' : genre,
			'itpStatus' : itpStatus,
			'form' : book_form
		}

		return render_template("submit.html", **templateData)


# pages inside a category
@app.route("/books/<book_slug>")
def book_display(book_slug):
	
	# get book by book_slug
	try:
		book = models.Book.objects.get(slug=book_slug)
	except:
		abort(404)

	# prepare template data
	templateData = {
		'book' : book
	}

	# render and return the template
	return render_template('book_entry.html', **templateData)



@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# slugify the title 
# via http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
	"""Generates an ASCII-only slug."""
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
	return unicode(delim.join(result))


# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	