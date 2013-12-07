import logging
import uuid
from redis import Redis

__author__ = 'patrickwalsh'


spoof = {
    "type": "FeatureCollection",
    "generator": "overpass-turbo",
    "copyright": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.",
    "timestamp": "2013-12-07T02:45:01Z",
    "features": [
        {
            "type": "Feature",
            "id": "node/25365457",
            "properties": {
                "@id": "node/25365457",
                "chchsid": "350",
                "highway": "traffic_signals",
                "source": "https://drive.google.com/file/d/0Bw_Qy6oHnvlKTk1xNmhIWTFiakk/edit?usp=sharing"
            },
            "geometry": {
                "type": "Point",
                "coordinates": [
                    172.6134007,
                    -43.5241967
                ]
            }
        }
]}

redis = Redis()



if __name__ == '__main__':
    main()