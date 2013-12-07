var http = require('http');
var url = require('url');
var sax = require('sax');
var util = require('util');
var redis = require("redis");
var uuid = require('uuid');

var redisClient = redis.createClient(6379, '192.168.16.189');
redisClient.on("error", function (err) {
    console.log("Error " + err);
});

var saxStream = require("sax").createStream(false, { });

var saNodes;
var current;
saxStream.on("opentag", function (node) {
    if (node.name === 'SAS') {
        saNodes = { };
        current = null;
    } else if (saNodes && node.name === 'SA') {
        var sid = node.attributes.SID;
        current = saNodes[sid];
        if (!current) {
            saNodes[sid] = current = {
                dsValues: [],
                sid: sid,
                timestamp: new Date().toISOString()
            };
        }
    } else if (current && node.name === 'LANE') {
        if (node.attributes.DS) {
            current.dsValues.push(node.attributes.DS);
        }
    }
});
saxStream.on("closetag", function (node) {
    if (saNodes && node === 'SAS') {
        for (var sid in saNodes) {
            var current = saNodes[sid];
            var average = 0;
            var max = 0;
            var min = 0;

            if (current.dsValues) {
                max = min = current.dsValues[0];
                current.dsValues.forEach(function (ds) {
                    average += ds;
                    if (max < ds) {
                        max = ds;
                    }
                    if (min > ds) {
                        max = ds;
                    } 
                });
                average /= current.dsValues.length;
            }

            var sidKey = 'sid:' + current.sid;
            redisClient.get(sidKey, function (err, iid) {
                function insertSid() {
                    console.log(iid + '= <values>');
                    redisClient.hmset(iid, 
                        'sid', current.sid,
                        'updated_at', current.timestamp,
                        'avg_cong', average,
                        'max_cong', max,
                        'min_cong', min
                    );
                }

                if (iid) {
                    insertSid();
                } else {
                    iid = 'iid:' + uuid.v4();
                    console.log(sidKey + '=' + iid);
                    redisClient.set(sidKey, iid, insertSid);
                }
            });
        }
    }
});

http.get('http://test:test@153.111.226.40:2412/transis/pushservice', function (res) {
  res.setEncoding('utf8');
  res.pipe(saxStream);
});

/*
client.hset("hash key", "hashtest 1", "some value", redis.print);
client.hset(["hash key", "hashtest 2", "some other value"], redis.print);
client.hkeys("hash key", function (err, replies) {
    console.log(replies.length + " replies:");
    replies.forEach(function (reply, i) {
        console.log("    " + i + ": " + reply);
    });
    client.quit();
});
*/