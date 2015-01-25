import json
import geohash

from app import app
import exceptions
import haversine

app.debug=True

"""
Function to check if foodcarts for geohash exists.

Param loc_geohash string a geohash.

Returns Bool True if foodcarts exist for geohash.
"""
def foodcarts_for_geohash_exists(loc_geohash):
  try:
    foodcarts_for_geohash_bucket = \
      app.config['datastore'].get_foodcarts_for_geohash_bucket()
    return foodcarts_for_geohash_bucket.get(loc_geohash).exists
  except Exception as e:
    app.logger.error("foodcarts_for_geohash_exists: Riak read exception")
    app.logger.error("%s", str(e))
    raise exceptions.FoodcartsRiakReadException(str(e))


"""
Function to return foodcarts for geohash.

Param loc_geohash string a geohash.

Returns Array of foodcarts for geohash.
"""
def get_foodcarts_for_geohash(loc_geohash):
  try:
    foodcarts_for_geohash_bucket = \
      app.config['datastore'].get_foodcarts_for_geohash_bucket()
    return foodcarts_for_geohash_bucket.get(loc_geohash).data
  except Exception as e:
    app.logger.error("get_foodcarts_for_geohash: Riak read exception")
    app.logger.error("%s", str(e))
    raise exceptions.FoodcartsRiakReadException(str(e))


"""
Function to compute foodcarts within radius
for a set of foodcarts within a broader geohash.

Param lat string lat.
Param long string long.
Param loc_geohash string geohash for given lat long.
Param radius float search radius.

Returns Json list of foodcart objects
"""
def compute_foodcarts_for_geohash(
  lat, long, loc_geohash, radius):

  foodcarts_in_radius = []

  try:
    foodcarts_bucket = \
      app.config['datastore'].get_foodcarts_bucket()
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

    return json.dumps(foodcarts_in_radius)
  except Exception as e:
    app.logger.error("compute_foodcarts_for_geohash: Riak read exception")
    app.logger.error("%s", str(e))
    raise exceptions.FoodcartsRiakReadException(str(e))

"""
Function to cache computed foodcarts in riak.

Param loc_geohash string geohash for given lat long.
Param computed_foodcarts_for_geohash 
  string json list of foodcart objects.
"""
def save_foodcarts_for_geohash(
  loc_geohash, computed_foodcarts_for_geohash):
  try:
    foodcarts_for_geohash_bucket = \
      app.config['datastore'].get_foodcarts_for_geohash_bucket()
    key = foodcarts_for_geohash_bucket.new(
      loc_geohash, data=computed_foodcarts_for_geohash)
    key.store()
  except Exception as e:
    app.logger.error("save_foodcarts_for_geohash: Riak write exception")
    app.logger.error("%s", str(e))
    raise exceptions.FoodcartsRiakWriteException(str(e))


"""
Function to verify lat long input.

Param lat float any latitude.
Param long float any longitude.

Returns Bool True if input is clean.
"""
def verify_input(lat, long):
  if lat and long:
    return True
  return False


"""
Function to get foodcarts data within a radius.

Param lat float any latitude.
Param long float any longitude.
Param radius float any search radius.

Returns Json list of foodcart objects.
"""
def get_foodcarts_within_radius(
  lat, long, radius=app.config['radius']):

  # verify input
  if not verify_input(lat, long):
    app.logger.error(
      "get_foodcarts_within_radius: \
        lat and long required")
    raise exceptions.FoodcartsInputException("lat long required.")
  
  # get 5 chars of geohash
  loc_geohash = geohash.encode(lat, long)[0:5]

  # if foodcarts for geohash exists return data
  if foodcarts_for_geohash_exists(loc_geohash):
    return get_foodcarts_for_geohash(loc_geohash)

  # if no foodcarts for geohash, compute
  computed_foodcarts_for_geohash = \
    compute_foodcarts_for_geohash(
      lat, long, loc_geohash, radius)

  # cache computed results for geohash
  save_foodcarts_for_geohash(
    loc_geohash, computed_foodcarts_for_geohash)

  return computed_foodcarts_for_geohash
