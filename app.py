import json
import itertools
import logging
import os
import uuid

__author__ = 'patrickwalsh'

from flask import Flask
import redis

app = Flask(__name__)
logger = logging.getLogger(__name__)

redis_url = os.environ.get('REDISTOGO_URL', 'redis://localhost:6379')

red = redis.from_url(redis_url)


IID_INDEX = 'index'

@app.route('/')
def hello():
    return os.environ.get('REDISTOGO_URL')

@app.route('/intersections')
def get_all_intersections():
    try:
        # all nodes are namespaced with iid
        nodes = red.keys('iid:*')
        feed = itertools.imap(red.hgetall, nodes)
        dehydrated = itertools.imap(dehydrate, feed)
        return json.dumps(dict(
            objects=list(dehydrated)
        ))
    except Exception as e:
        logger.exception(e)


def dehydrate(node):
    keys = ['sid', 'id', 'updated_at', 'lat', 'lon', 'osm_id', 'min_cong', 'max_cong', 'avg_cong']
    data = {key: node.get(key, None) for key in keys}

    return data


@app.route('/update_osm')
def update_osm():
    with open('export.geojson', 'w') as f:
        features = f['features']
        for feat in features:
            osm_id = feat['id'].split('/')[1]
            sid = feat['props']['chchsid']
            lon, lat = feat['geometry']['coordinates']

            assign(sid, lat=lat, lon=lon, osm_id=osm_id)

def assign(sid, **mapping):
    sid_key = 'sid:'+sid
    iid_key = red.get('sid:'+sid)
    if not iid_key:
        iid_key = 'iid:' + uuid.uuid4()
        red.set(sid_key, iid_key)

    mapping.update(dict(sid=sid))
    red.hmset(iid_key, mapping)

if __name__ == '__main__':
    app.run()