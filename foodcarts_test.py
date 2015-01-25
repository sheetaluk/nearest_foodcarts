import os
import riak
import unittest
import json
from mock import MagicMock, Mock, patch, create_autospec

from app import app
from app import foodcarts
from app import datastore
from app import exceptions


"""
Class that does the setUp for interactions with Riak.
"""
class FoodcartsTestCase(unittest.TestCase):
  def setUp(self):
    self.mock_client = riak.client.RiakClient(
      "pbc", {}, {}, {}, 1)
    self.mock_bucket_type = riak.bucket.BucketType(
      self.mock_client, "name2")
    self.mock_bucket = riak.bucket.RiakBucket(
      self.mock_client, "name3", self.mock_bucket_type)
    self.mock_key = riak.riak_object.RiakObject(
      self.mock_client, self.mock_bucket)
    self.mock_obj = riak.riak_object.RiakObject(
      self.mock_client, self.mock_bucket, "objname")
    self.mock_data = {
      "latitude":"37.7901633841957", \
      "longitude":"-122.39754345993"}
    self.mock_obj.data = self.mock_data

    app.config['datastore'] = datastore.Datastore(
      self.mock_client)
    app.config['datastore'].get_foodcarts_for_geohash_bucket = MagicMock(
      return_value=self.mock_bucket)
    app.config['datastore'].get_foodcarts_bucket = MagicMock(
      return_value=self.mock_bucket)
    self.mock_bucket.new = MagicMock(
      return_value=self.mock_key)
    self.mock_bucket.get_index = MagicMock(
      return_value={self.mock_key})
    self.mock_bucket.get = MagicMock(
      return_value=self.mock_obj)
    self.mock_bucket.data = self.mock_data
    self.mock_key.store = MagicMock(
      return_value=1)
    self.mock_key.encode = MagicMock(
      return_value="some string")

  
"""
Tests for foodcarts_for_geohash_exists().
"""
class FoodcartsForGeohashExistsTestCase(FoodcartsTestCase):
  def test_exists(self):
    result = foodcarts.foodcarts_for_geohash_exists(
      'foo')

    self.mock_bucket.get.assert_called_with('foo')

  def test_exists_exception(self):
    self.mock_bucket.get = Mock(
      side_effect=exceptions.FoodcartsRiakReadException(
        'ex'))
    self.assertRaises(
      exceptions.FoodcartsRiakReadException, \
      foodcarts.foodcarts_for_geohash_exists, \
      'foo')


"""
Tests for get_foodcarts_for_geohash().
"""
class GetFoodcartsForGeohashTestCase(FoodcartsTestCase):
  def test_get(self):
    result = foodcarts.get_foodcarts_for_geohash("objname")
    self.mock_bucket.get.assert_called_with("objname")
    self.assertTrue(result ==self.mock_data)

  def test_get_exception(self):
    self.mock_bucket.get = Mock(
      side_effect=exceptions.FoodcartsRiakReadException(
        "ex"))
    self.assertRaises(
      exceptions.FoodcartsRiakReadException, \
      foodcarts.get_foodcarts_for_geohash, \
      "objname")


"""
Tests for compute_foodcarts_for_geohash().
"""
class ComputeFoodcartsForGeohash(FoodcartsTestCase):
  def test_compute(self):
    expected_result = []
    expected_result.append(self.mock_data)
    expected_result = json.dumps(expected_result)

    result = foodcarts.compute_foodcarts_for_geohash(
      37.776775, -122.416791, 'foo', 3)

    self.mock_bucket.get_index.assert_called_with(
      "geohash_bin", "foo")
    self.mock_bucket.get.assert_called_with(
      "some string")
    self.assertTrue(result == expected_result)

  def test_compute_no_nearby_foodcarts(self):
    result = foodcarts.compute_foodcarts_for_geohash(
      27.183212, -80.191340, 'foo', 1)

    self.mock_bucket.get_index.assert_called_with(
      "geohash_bin", "foo")
    self.mock_bucket.get.assert_called_with(
      "some string")
    self.assertTrue(result == '[]')

  def test_compute_exception(self):
    self.mock_bucket.get = Mock(
      side_effect=exceptions.FoodcartsRiakReadException(
        'ex'))
    self.assertRaises(
      exceptions.FoodcartsRiakReadException, \
      foodcarts.compute_foodcarts_for_geohash, \
      1.0, \
      2.0, \
      'foo', \
      1)

  
"""
Tests for save_foodcarts_for_geohash().
"""
class SaveFoodcartsForGeohashTestCase(FoodcartsTestCase):
  def test_save(self):
    foodcarts.save_foodcarts_for_geohash('foo', '[]')

    self.mock_bucket.new.assert_called_with(
      'foo', data='[]')
    self.mock_key.store.assert_called_with()

  def test_save_exception(self):
    self.mock_bucket.new = Mock(
      side_effect=exceptions.FoodcartsRiakWriteException(
        'ex'))
    self.assertRaises(
      exceptions.FoodcartsRiakWriteException, \
      foodcarts.save_foodcarts_for_geohash, \
      'foo', \
      '[]')


"""
Tests for verify_input().
"""
class VerifyInputTestCase(unittest.TestCase):
  def test_with_lat_and_long(self):
    assert foodcarts.verify_input(1.0, 2.0) == True

  def test_with_lat_and__no_long(self):
    assert foodcarts.verify_input(1.0, None) == False

  def test_with_no_lat_and_long(self):
    assert foodcarts.verify_input(None, 2.0) == False


"""
Tests for get_foodcarts_within_radius()
"""
class GetFoodcartsWithinRadiusTestCase(FoodcartsTestCase):
  def test_get_from_cache(self):
    foodcarts.foodcarts_for_geohash_exists = MagicMock(
      return_value=True)
    foodcarts.get_foodcarts_for_geohash = MagicMock(
      return_value=self.mock_data)

    results = foodcarts.get_foodcarts_within_radius(
      37.776775, -122.416791, 1)

    self.assertTrue(results == self.mock_data)

  def test_get_compute_data(self):
    foodcarts.foodcarts_for_geohash_exists = MagicMock(
      return_value=False)
    foodcarts.compute_foodcarts_for_geohash = MagicMock(
      return_value=self.mock_data)

    results = foodcarts.get_foodcarts_within_radius(
      37.776775, -122.416791, 1)

    self.assertTrue(results == self.mock_data)

if __name__ == '__main__':
    unittest.main()
