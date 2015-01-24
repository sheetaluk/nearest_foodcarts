import os

from flask import Flask

app = Flask(__name__)

app.config['radius'] = 2 #km

app.config['riak_node'] = '54.164.165.43'
app.config['riak_http_port'] = 8098
app.config['riak_protocol'] = 'http'
app.config['riak_foodcarts_bucket'] = 'foodcarts_test3'
app.config['riak_foodcarts_for_geohash_bucket'] = \
  'foodcarts_for_geohash_test5'

from app import api
