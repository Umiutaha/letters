import urllib
import urllib2
import json
from hashlib import md5
from datetime import datetime
from django.test import TestCase
from django.conf import settings


def get_uniq_hash(request):
    uniq_hash = md5(str(datetime.now()) + request.user.username).hexdigest()[:7]
    return uniq_hash


def send_event(event_type, event_data, session_id, user=None):
    if isinstance(event_data, dict):
        event_data = json.dumps(event_data)
    to_send = {
        'event': event_type,
        'data': event_data,
        'session_id': session_id,
        'user': user
    }
    urllib2.urlopen(settings.ASYNC_BACKEND_URL, urllib.urlencode(to_send))


class MongoTestCase(TestCase):
    """
        TestCase class that clear the collection between the tests
    """
    mongodb_name = 'test_%s' % settings.MONGO_DATABASE_NAME

    def _pre_setup(self):
        from mongoengine.connection import connect, disconnect
        disconnect()
        connect(self.mongodb_name, port=settings.MONGO_PORT)
        super(MongoTestCase, self)._pre_setup()

    def _post_teardown(self):
        from mongoengine.connection import get_db, disconnect
        database = get_db()
        for collection in database.collection_names():
            if collection == 'system.indexes' or collection == 'english_words':
                continue
            database.drop_collection(collection)
        disconnect()
        super(MongoTestCase, self)._post_teardown()
