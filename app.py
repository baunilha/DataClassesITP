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




# ----------- Lists -----------


# Create the lists that match the name of the ListField in the models.py
categories = ['web','physical computing','programming','video','music','installation','social media','developing nations','business','networks', 'fabrication', 'theory', 'art', 'data', 'sound']




# --------- ROUTES ----------


# this is our MAIN PAGE
@app.route("/")
def index():
	# render the template, retrieve 'courses' from the database
	return render_template("main.html", courses=models.Course.objects())



# this is our SUBMIT COURSES PAGE
@app.route("/submit", methods=['GET','POST'])
def submit():

	app.logger.debug(request.form.getlist('categories'))

	# get Idea form from models.py
	course_form = models.CourseForm(request.form)
	
	if request.method == "POST" and course_form.validate():
	
		now = datetime.datetime.now()

	# get form data - create new course
		course = models.Course()
		
		course.title = request.form.get('title')
		course.description = request.form.get('description','')
		course.instructor = request.form.get('instructor')
		course.slug = slugify(course.title + "-" + course.instructor + "-" + now.strftime("%f"))
		course.semester = request.form.get('semester')
		course.year = request.form.get('year')
		course.categories = request.form.getlist('categories')
		# course.units = request.form.get('units')
	
		course.save()

		return redirect('/courses/%s' % course.slug)

	else:

		if request.form.getlist('categories'):
			for c in request.form.getlist('categories'):
				course_form.categories.append_entry(c)

		templateData = {
			'courses' : models.Course.objects(),
			'categories' : categories,
			'form' : course_form
		}

		return render_template("submit.html", **templateData)



# COURSES PAGE
@app.route("/courses/<course_slug>")
def course_display(course_slug):

	# get idea by idea_slug
	try:
		course = models.Course.objects.get(slug=course_slug)
	except:
		abort(404)


	# prepare template data
	templateData = {
		'course' : course
	}

	# render and return the template
	return render_template('idea_entry.html', **templateData)



# Display all courses for a SPECIFIC CATEGORY
@app.route("/category/<cat_name>")
def by_category(cat_name):

	# try and get courses where cat_name is inside the categories list
	try:
		courses = models.Course.objects(categories=cat_name)

	# not found, abort w/ 404 page
	except:
		abort(404)

	# prepare data for template
	templateData = {
		'current_category' : {
			'slug' : cat_name,
			'name' : cat_name.replace('_',' ')
		},
		'courses' : courses,
		'categories' : categories
	}

	# render and return template
	return render_template('category_listing.html', **templateData)
	


# Comments Page
@app.route("/courses/<course_id>/comment", methods=['POST'])
def course_comment(course_id):

	comment = request.form.get('comment')

	if comment == '':
		# no name or comment, return to page
		return redirect(request.referrer)


	#get the course by id
	try:
		course = models.Course.objects.get(id=course_id)
	except:
		# error, return to where you came from
		return redirect(request.referrer)


	# create comment
	comment = models.Comment()
	comment.comment = request.form.get('comment')
	
	# append comment to course
	course.comments.append(comment)

	# save it
	course.save()

	return redirect('/courses/%s' % course.slug)



# Errors...
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404



# Slugify the title to create URLS
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



	