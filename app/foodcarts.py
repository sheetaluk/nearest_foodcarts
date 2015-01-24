import riak
import json
import geohash

from app import app

import haversine

riak_client = riak.RiakClient(
  protocol=app.config['riak_protocol'], \
  host=app.config['riak_node'], \
  http_port=app.config['riak_http_port'])
foodcarts_bucket = riak_client.bucket(
  app.config['riak_foodcarts_bucket'])
foodcarts_for_geohash_bucket = riak_client.bucket(
  app.config['riak_foodcarts_for_geohash_bucket'])

"""
Function to get foodcarts data within a radius.

Param lat float any latitude.
Param long float any longitude.
Param radius float any search radius.

Returns Json list of foodcart objects.
"""
def get_foodcarts_within_radius(
  lat, long, radius=app.config['radius']):

  if not lat or not long:
    app.logger.error(
      "get_foodcarts_within_radius: lat and long required")
    raise Exception("lat and long required")

  loc_geohash = geohash.encode(lat, long)[0:5]
  foodcarts_in_radius = []

  # if already calculated for geohash, return calculated data
  fetched_foodcarts_for_geohash = \
    foodcarts_for_geohash_bucket.get(loc_geohash)
  if fetched_foodcarts_for_geohash.exists:
    return fetched_foodcarts_for_geohash.data

  # if not yet calculated for geohash, compute nearest foodcarts
  foodcart_keys = foodcarts_bucket.get_index(
    "geohash_bin", loc_geohash)
  for foodcart_key in foodcart_keys:
    foodcart_data = foodcarts_bucket.get(
      foodcart_key.encode('utf8')).data

    if haversine.haversine_distance(
      (lat, long),
      (float(foodcart_data['latitude']),
        float(foodcart_data['longitude']))) \
      <= radius:
      foodcarts_in_radius.append(foodcart_data)

  # cache computed results for geohash
  foodcarts_in_radius_json = \
    json.dumps(foodcarts_in_radius)
  key = foodcarts_for_geohash_bucket.new(
    loc_geohash, data=foodcarts_in_radius_json)
  key.store()

  return foodcarts_in_radius_json
