"""sample simple example
"""

import pymongo
from datetime import datetime
from nanomongo import NanoMongo

db =  pymongo.Connection().test

class BlogPost(NanoMongo):
    collection = db.blogpost
    _insert_defaults = {
        "date_created" : lambda self: datetime.utcnow(),
    }

    @classmethod 
    def latest(cls):
        return cls.find( { "active" : True } ) \
            .sort( 'date_created', -1 ) \
            .limit(15)

if __name__ == '__main__':
    p = BlogPost()
    p.title = "Hello world"
    p.body = "This is the first post"
    p.tags = [ "test", ]
    p.active = True
    p.save()
    
    print "Created new post, with id", p._id

    print "-------------------"

    print "Latest posts below"
    for item in BlogPost.latest():
        print item
