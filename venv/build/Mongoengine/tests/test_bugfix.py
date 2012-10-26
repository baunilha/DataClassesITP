import unittest
from mongoengine import *
from bson import ObjectId
from mongoengine.tests import query_counter
import datetime


class Test(unittest.TestCase):

    def setUp(self):
        conn = connect(db='mongoenginetest')

    def test_list_item_dereference(self):
        """Ensure that DBRef items in ListFields are dereferenced.
        """
        class Post(Document):
            slug = StringField(primary_key=True)
            author = ReferenceField('User', dbref=False)
            likes = ListField(ReferenceField('User'))

        class User(Document):
            email = StringField(required=True)
            name = StringField(max_length=50)

        User.drop_collection()
        Post.drop_collection()

        user = User(email='ross@10gen.com').save()
        Post(slug='/test', author=user).save()

        Post._collection.update({'slug': '/test'}, {"$set": {"author": "%s" % user.pk}})

        # self.assertEqual(1, Post.objects(author="%s" % user.pk).count())
        # self.assertEqual(1, Post.objects(author=user.pk).count())
        # import ipdb; ipdb.set_trace();

        # col = Post._collection()
        # for doc in col.find():
        #     col.update({"_id": doc._id}, {"$set": {"author": ObjectId(doc.author)}})

if __name__ == '__main__':
    unittest.main()
