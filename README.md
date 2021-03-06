Problem
--------
[Create a service that tells the user what types of food trucks might be found near a specific location on a map.](https://github.com/uber/coding-challenge-tools/blob/master/coding_challenge.md)

Solution
---------
1. [Demo](http://uber.foodcarts.com.s3-website-us-east-1.amazonaws.com/)
2. curl -i 'http://vast-castle-9076.herokuapp.com/api/v1.0/nearest_foodcarts?user_lat=37.776775&user_long=-122.416791'

This web application is an interactive map, which marks foodcarts near a user marked location, represented by a pin.
The list of foodcarts will refresh when the user updates his location, by clicking on any point in the map.
The name, address and types of foods served will be displayed when the user clicks on any of the foodcart markers.
The map has a default user location set in SFO.

###Notes:
We have to decide what nearby means. Are two lat&longs near each other based on distance? Or is it how much time it takes to get from one lat&long to an other. I have assumed the former, but in reality it might not apply to all cities.  
Ex: Grid system of roads vs concentric  
Nearby might also be different for people who walk and people using vehicles.  
Ex: NYC has a number of one ways, NY and NJ are close but seperated by the Hudson.  

Architecture
-------------
Each foodcart object is added to the foodcarts bucket and indexed with a short geohash (first 5 chars).
This allows the backend to retrieve the foodcarts which are in the same approximate area of the user input lat&lng.
Once the backend retrieves a subset of the foodtrucks in the database, 
  it calculates the haversine distance between each of them to the userpin.
foodcarts which are within 1km(configurable) of userpin are returned to the client in a json format.
The results are cached in a second Riak bucket against a longer Geohash of the user lat&long (8 chars).

Focus
------
Full Stack.

I have tried to align the application with the Uber stack. I am not very familiar with Backbone, Python or Riak, but
enjoy the challenge of learning new things.

### Frontend
Backbone: I don't have much experience with Backbone,
but it is lightweight and quite easy to understand.

### Backend
Flask and Python: I don't have much experience with Flask or Python.
It is lightweight and easy to setup.

### Database
Riak: I don't have much experience with Riak.
It is fault tolerent, distributed and highly available. When my application gets the million users it derserves,
scalability and availability will be a cinch.

What I could do in addition
----------------------------
1. Integration tests: I have to figure out how to write integration tests for my Flask app. 
2. Exception handling: I raise exceptions and propogate them upwards. It might be worth while to discuss how we want the app to behave in case of different exceptions/error.
3. Seperate dev/test and prod configurations. 
4. Additional features for current dataset:
     1. User can search for foodcart.
     2. User can see foodcart ratings when available.
     3. User can see a list of foodcarts instead of having to click on each marker to see info.
     4. User sees only valid and current foodcarts.
     5. User can input radius to fetch foodcarts for.
5. Find a human code reviewer.

What I could do differently
----------------------------
1. Computing the nearby foodcarts can be done a little better. One other way would be to search for foodcarts within    a tight geohash string(long) and then truncate the geohash 1 character at a time till we have a satisfactory
   number of results, which we can then return to the user.
2. I have not used any build tools for the app. 
3. The JS could be refactored into seperate files, library files downloaded and then minified, concatenated etc.
   The backbone app could be refactored to possibly use a marker model and view.
4. I am not very familiar with Flask and hence the directory structure and file organisation might
   look a little strange.
5. Change all usage of [fF]oodcart to [fF]oodtruck. It was a mistake I made early and discovered late.

Misc
-----
My husband had used my laptop sometime back for a pet project and after my first commit I realised that the ssh keys
were still tied to his account.
amr46 is not a contributor.  
I did not write the Haversine distance function.
