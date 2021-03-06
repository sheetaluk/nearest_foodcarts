import os
import riak
from flask import Flask
from datastore import Datastore
from flask.ext.cors import CORS

app = Flask(__name__)

cors = CORS(app)

app.config['radius'] = 1 #km

app.config['riak_node'] = '54.164.165.43'
app.config['riak_http_port'] = 8098
app.config['riak_protocol'] = 'http'
app.config['riak_foodcarts_bucket'] = 'foodcarts_prod'
app.config['riak_foodcarts_for_geohash_bucket'] = \
  'foodcarts_for_geohash_prod'

riak_client = riak.RiakClient(
  protocol=app.config['riak_protocol'], \
  host=app.config['riak_node'], \
  http_port=app.config['riak_http_port'])
app.config['datastore'] = Datastore(riak_client)

from app import api
