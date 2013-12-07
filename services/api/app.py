import json
import itertools
import logging

__author__ = 'patrickwalsh'

from flask import Flask
from redis import Redis

app = Flask(__name__)
logger = logging.getLogger(__name__)

redis = Redis()


IID_INDEX = 'index'

@app.route('/intersections')
def get_all_intersections():
    try:
        nodes = redis.smembers(IID_INDEX)

        feed = itertools.imap(redis.hgetall, nodes)
        dehydrated = itertools.imap(dehydrate, feed)
        return json.dumps(dict(
            objects=list(dehydrated)
        ))
    except Exception as e:
        logger.exception(e)


def dehydrate(node):
    keys = ['sid', 'iid', 'timestamp', 'lat', 'lon', 'osm_id', 'min_cong', 'max_cong', 'avg_cong']

    data = {key: node.get(key, None) for key in keys}

    # translate
    data['id'] = data['iid']
    del data['iid']

    return data

if __name__ == '__main__':
    app.run()