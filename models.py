# -*- coding: utf-8 -*-
from mongoengine import *

from flask.ext.mongoengine.wtf import model_form
from datetime import datetime


class Book(Document):
    title = StringField(required=True, max_length=120, verbose_name="title")
    slug = StringField()
    author = StringField(required=True, max_length=120, verbose_name="author")
    image = StringField(max_length=50)

    # Book type and genre are lists of Strings
    bookType = ListField(StringField(max_length=30))
    genre = ListField(StringField(max_length=30))

    description = StringField(max_length=500)
    owner = StringField(required=True, max_length=200, verbose_name="owner")

    # Email is another different field
    email = EmailField(required=True, max_length=100, verbose_name="email")

    # itpStatus is a list of Strings
    itpStatus = ListField(StringField(max_length=30))

BookForm = model_form(Book)