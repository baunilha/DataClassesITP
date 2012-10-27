# -*- coding: utf-8 -*-
from mongoengine import *

from flask.ext.mongoengine.wtf import model_form
from datetime import datetime


class Comment(EmbeddedDocument):
	name = StringField(required=False)
	comment = StringField()
	rating = IntField()
	timestamp = DateTimeField(default=datetime.now())

class Course(Document):

	title = StringField(max_length=120, required=True, verbose_name="Class name")
	description = StringField()
	slug = StringField()
	instructor = StringField(required=True)
	semester = StringField(choices = (('spring','Spring'),('fall','Fall')) )
	year = StringField()
	categories = ListField( StringField() )
	units = StringField(choices = ( ('2','2'), ('4','4') ), required=False )
	# rating

	# Comments is a list of Document type 'Comments' defined above
	comments = ListField( EmbeddedDocumentField( Comment ) )


CourseForm = model_form(Course)

	

