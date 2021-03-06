# -*- coding: utf-8 -*-

import os, datetime
import re
from unidecode import unidecode

from flask import jsonify

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
categories = ['3D','Analog Craft','Animation','Art','Audio','Biology','Business','Computer Vision','Critique','Data','Children','Design','Developing Nations','Education','Environment','Exhibit','Fabrication','Foundation','Game','Installation','Internet','Journalism','Mobile','Music','Narrative','Networks','Performance','Physical Computing','Politics','Programming','Projection','Science','Social Media','Seminar','Sustainable','Teamwork', 'Theory', 'Video','Visualization','Wearable','Web']

# --------- ROUTES ----------


# this is our MAIN PAGE
@app.route("/", methods= ['GET', 'POST'])
def index():

	semester = "Fall"
	year = "2013"

	filtered_courses = []
	all_courses = models.Course.objects()

	all_courses_sort = sorted(all_courses, key=lambda k: k['title']) 

	for c in all_courses_sort:
		if c.semester.lower() == semester.lower() and c.year == year:
			filtered_courses.append(c)

	templateData = {
		'courses' : filtered_courses,
		'semester' : [semester, year]
	}
	return render_template("main.html", **templateData)

# Search Page
@app.route("/search", methods=['POST'])
def search():

	search_courses = []
	search_str = request.form.get('search')

	search_display = models.Course.objects()
	search_display = models.Course.objects(title__icontains=search_str)

	for s in search_display:
		search_courses.append(s)

	templateData = {
		'courses' : search_courses
	}

	return render_template("search.html", **templateData)


# filtering semester and year to show in the main page
@app.route("/filter", methods=['POST'])
def filter():

	filtered_courses = []
	filter_str = request.form.get('filter')
	both = filter_str.split(",")
	semester = both[0]
	year = both[1]

	all_courses = models.Course.objects()
	all_courses_sort = sorted(all_courses, key=lambda k: k['title']) 

	for c in all_courses_sort:
		if c.semester.lower() == semester.lower() and c.year == year:
			filtered_courses.append(c)

	templateData = {
		'courses' : filtered_courses,
		'semester' : [semester, year]
	}

	return render_template("main.html", **templateData)

# this is our SUBMIT COURSES PAGE
@app.route("/submit", methods=['GET','POST'])
def submit():

	app.logger.debug(request.form.getlist('categories'))

	# get Idea form from models.py
	course_form = models.CourseForm(request.form)
	
	if request.method == "POST" and course_form.validate():
	
		# now = datetime.datetime.now()

	# get form data - create new course
		course = models.Course()
		
		course.title = request.form.get('title')
		course.description = request.form.get('description','')
		course.instructor = request.form.get('instructor')
		course.semester = request.form.get('semester')
		course.year = request.form.get('year')
		course.slug = slugify(course.title + "-" + course.instructor + "-" + course.semester + "-" + course.year)
		course.categories = request.form.getlist('categories')
	
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

	tag_str = ", ".join(course.tags)

	# prepare template data
	templateData = {
		'course' : course,
		'tags' : tag_str
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

	like = request.form.get('like')
	learn = request.form.get('learn')
	recommendation = request.form.get('recommendation')
	tags = request.form.get('tags')
	app.logger.debug(tags) #works here

	if like == '' or learn == '' or recommendation == '' or tags== '':
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
	comment.like = request.form.get('like')
	comment.learn = request.form.get('learn')
	comment.recommendation = request.form.get('recommendation')
	
	# append comment to course
	course.comments.append(comment)

	# add tags
	tags = request.form.get('tags')
	app.logger.debug(tags) #doesn't work here
	course.tags.append(tags) #not working

	# save it
	course.save()

	return redirect('/courses/%s' % course.slug)

# Data in JSON
@app.route('/data/courses')
def data_courses():

	# query for the courses - returning alphabetical order
	all_courses = models.Course.objects()
	all_courses_order = sorted(all_courses, key=lambda k: k['title'])

	if all_courses_order:

		# list to hold courses
		public_courses = []

		#prep data for json
		for c in all_courses_order:

			tmpCourse = {
				'title' : c.title,
				'description' : c.description,
				'instructor' : c.instructor,
				'semester' : c.semester,
				'year' : c.year,
				'categories' : c.categories,
				'tags' : c.tags
			}

			# reviews/comments - our embedded documents
			tmpCourse['comments'] = [] # list - will hold all comment dictionaries

			# loop through courses reviews/comments
			for m in c.comments:
				comment_dict = {
					'like' : m.like,
					'learn' : m.learn,
					'recommendation' : m.recommendation,
					'timestamp' : str( m.timestamp )
				}

				# append comment_dict to ['comments']
				tmpCourse['comments'].append(comment_dict)

			# insert idea dictionary into public_courses list
			public_courses.append( tmpCourse )

		# prepare dictionary for JSON return
		data = {
			'status' : 'OK',
			'all_courses_order' : public_courses
		}

		# jsonify (imported from Flask above)
		# will convert 'data' dictionary and set mime type to 'application/json'
		return jsonify(data)

	else:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve ideas'
		}
		return jsonify(error)


		
@app.route("/killalloftype")
def killalloftype():
# 	all_courses = models.Course.objects()
# 	for c in all_courses:
# 		if '2013' in c.year:
# 			c.delete()
# 			app.logger.debug( "DELETED: " + c.title )

	return redirect("/")

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



	