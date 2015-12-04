echo '{"type":"FeatureCollection","features":'"$(cat tweets* | jq 'select(.geo)| {type: "Feature", geometry:{type:"Point", coordinates:[.geo.coordinates[1],.geo.coordinates[0]]},properties:{tweet_body:.text,handle:.user.screen_name}}' | jq -s .)"'}' > geoData.json 

