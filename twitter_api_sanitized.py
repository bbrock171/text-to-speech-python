from twitter import *
import random, time, itertools, sqlite3, datetime, urllib
import numpy as np
import ujson as json

QUERY_INTERVAL = 0.009 # DD
RADIUS = '1mi' # No rhyme or reason to this radius. The API was returning bad results in meters. 

MINX = -77.0956
MAXX = -77.0347
MINY = 38.7874
MAXY = 38.8689

TABLE = 'tweets'
SERVICE = 'twitter'

# List of API credentials
CREDS = []
CREDS += [dict(access_token ='<your access token>',
               access_token_secret ='<your token secret>',
               consumer_key ='<your consumer key>',
               consumer_secret = '<your consumer secret>'
               )]
CREDS += [dict(access_token ='<your access token>',
               access_token_secret ='<your token secret>',
               consumer_key ='<your consumer key>',
               consumer_secret = '<your consumer secret>'
               )]
CREDS += [dict(access_token ='<your access token>',
               access_token_secret ='<your token secret>',
               consumer_key ='<your consumer key>',
               consumer_secret = '<your consumer secret>'
               )]
# CREDS += [...

# Create database
con = sqlite3.connect('alexandria_test')
cur = con.cursor()
try:
	cur.execute('CREATE TABLE {table_name} (date text, service text, x float, y float, payload text)'.format(table_name=TABLE))
	con.commit()
except Exception as er:
	pass

# Turns bounding box into grid of points
def create_grid(minx, maxx, miny, maxy, interval):
	# Create lists of x coords and y coords evenly spaced between min and max values
	xs = np.arange(minx, maxx, interval)
	ys = np.arange(miny, maxy, interval)

	# Create all-pairs point list.
	coords = []
	for x in xs:
		for y in ys:
			coords += [(round(x, 6), round(y, 6))]
	print "Number of queries: " + str(len(coords))

	# Randomize query list
	coords = [coords[i] for i in random.sample(xrange(len(coords)), len(coords))]
	time.sleep(1)
	return coords


coords = create_grid(MINX, MAXX, MINY, MAXY, QUERY_INTERVAL)

cred_iter = itertools.cycle(CREDS)

# Iterate through point grid querying API for each. 
for index, coord in enumerate(coords):
	# Switch API keys every 15 calls. Twitter Limits to 15 calls every 15 minutes.
	if index % 15 == 0:
		cred = cred_iter.next()
		t = Twitter(auth=OAuth(cred['access_token'],
		                       cred['access_token_secret'],
		                       cred['consumer_key'],
		                       cred['consumer_secret']))
	
	x, y = coord
	try:
		print '{y},{x},{radius}'.format(y=y, x=x, radius=RADIUS)
		result = t.search.tweets(q='food OR eat OR dinner OR delicious OR restaurant', 
				result_type='mixed', geocode='{y},{x},{radius}'.format(y=y, x=x, 
				radius=RADIUS), count=100)
		
		sql = 'INSERT INTO {table_name} VALUES (?,?,?,?,?)'.format(table_name=TABLE)
		params = datetime.date.today(), SERVICE, x, y, json.dumps(result)
		cur.execute(sql, params)
		con.commit()

		for tweet_count, tweet in enumerate(result['statuses']):
			with open('output/tweets_' + str(index + 1) + '_' + str(tweet_count + 1) + '.json', 'w') as f:
				f.write(json.dumps(tweet))
	except TwitterHTTPError as er:
		print er.message

	time.sleep(1) # See comment above about API limits. 

con.close()











