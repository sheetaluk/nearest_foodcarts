import os
import riak
import json
import requests
import geohash

"""
Function to check if a foodcart has status approved.

Param foodcart_dict dict a foodcart object.

Returns Bool True if approved.
"""
def has_status_approved(foodcart_dict):
  return foodcart_dict['status'].lower() == 'approved'

"""
Function to check if a foodcart has lat and long.

Param foodcart_dict dict a foodcart object.

Returns Bool True if has lat and long.
"""
def has_lat_long(foodcart_dict):
  if 'latitude' in foodcart_dict and \
    'longitude' in foodcart_dict:
    return True
  return False

riak_client = riak.RiakClient(
  protocol='http', host='54.164.165.43', http_port=8098)
foodcart_bucket = riak_client.bucket('foodcarts_test3')

foodcarts_json_data = requests.get(
    'http://data.sfgov.org/resource/rqzj-sfat.json')
foodcarts_dict = json.loads(foodcarts_json_data.text)
foodcarts_dict_len = len(foodcarts_dict)
for i in range(foodcarts_dict_len):
  if has_status_approved(foodcarts_dict[i]) and \
    has_lat_long(foodcarts_dict[i]):
    key = foodcart_bucket.new(
      foodcarts_dict[i]['permit'], data=foodcarts_dict[i])
    key.add_index(
      'geohash_bin', geohash.encode(
        float(foodcarts_dict[i]['latitude']), \
        float(foodcarts_dict[i]['longitude']))[0:5])
    key.store()
