import json
import os
import logging
import datetime
import time

# Parameters
IN_FILE = ''
OUT_FILE = ''
OUT_PROFILE = ''
LOG_FILE = ''

# Dates that matter (see paper)
aug2016 = datetime.date(2016,8,16) # Everything before this is not kept
aug2017 = datetime.date(2017,8,17) # Nothing after this is considered 'home'

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=LOG_FILE,
                    filemode='a')
					
# Function to write headers; called if OUT_FILE does not already exist
def startfile(file):
	with open(file, 'a+', encoding='utf-8') as outfile:	
			outfile.write(
				'user_id' + ',' +
				'tweet_id' + ',' +
				'rt' + ',' +
				'year' + ',' +
				'month' + ',' +
				'date' + ',' +
				'time' + ',' +
				'home' + ',' +
				'long' + ',' + 
				'lat' + ',' +
				'place'
			)
			outfile.write('\n')

try:
	if os.stat(OUT_FILE).st_size == 0:
		startfile(OUT_FILE)
except OSError:
	startfile(OUT_FILE)

# Function to write headers, called if OUT_PROFILE does not already exist
def startoutprofile(file):
	with open(file, 'a+', encoding='utf-8') as outprofile:
		outprofile.write(
			'user_id' + ',' +
			'lang' + ',' +
			'created_year' + ',' +
			'created_month' + ',' +
			'created_date' + ',' +								
			'followers' + ',' +
			'friends' + ',' +
			'location' + ',' +
			'toonew'
		)
		outprofile.write('\n')
	
try:
	if os.stat(OUT_PROFILE).st_size == 0:
		startoutprofile(OUT_PROFILE)
except OSError:
	startoutprofile(OUT_PROFILE)


# Parsing json data
n_tweets_parsed = 0
n_users_parsed = 0
user=''
with open(IN_FILE, 'r') as data:
	with open(OUT_FILE, 'a+', encoding='utf-8') as outfile:
		for x in data: # Reading each json object
			try:
				datastore = json.loads(x)
				# Parse tweet only if it is on or after August 16, 2016
				date = time.strptime(str(datastore['created_at'])[4:10]+str(datastore['created_at'])[26:],'%b %d%Y')
				created = datetime.date(date[0],date[1],date[2])
				if created >= aug2016:
					# If account of current tweet is different from account of last tweet, write to user outfile
					if str(datastore['user']['id']) != user:
						# Update account to 'current' account
						user = str(datastore['user']['id'])
						# Check account creation date, if after August 17, 2017, set as 'toonew'
						dateuser = time.strptime(str(datastore['user']['created_at'])[4:10]+str(datastore['user']['created_at'])[26:],'%b %d%Y')
						createduser = datetime.date(dateuser[0],dateuser[1],dateuser[2])
						if createduser >= aug2017:
							toonew = 1
						else: 
							toonew = 0
						with open(OUT_PROFILE, 'a+', encoding='utf-8') as outprofile:
							outprofile.write(
								user + ',' +
								str(datastore['user']['lang']) + ',' +
								str(dateuser[0]) + ',' +
								str(dateuser[1]) + ',' +
								str(dateuser[2]) + ',' +								
								str(datastore['user']['followers_count']) + ',' +
								str(datastore['user']['friends_count']) + ',' +
								'"' + str(datastore['user']['location']) + '"' + ',' +
								str(toonew)
							)
							outprofile.write('\n')
						n_users_parsed += 1
					# Is retweet?
					if str(datastore['text'])[0:2] == 'RT':
						rt = 1
					else:
						rt = 0
					# What are exact longitude and latitude, if any?
					coord = datastore['coordinates']
					if coord != None:
						coord = coord['coordinates']
					else:
						coord = ['','']
					# Store Twitter place id, if any
					place = datastore['place']
					if place != None:
						place = place['id']
					else:
						place = ''
					# Is the tweet between 10pm and 8am UTC-5?
					if int(datastore['created_at'][11:13]) > 3 and int(datastore['created_at'][11:13]) < 13 and created < aug2017:
						home = 1
					else:
						home= 0
					
					# Write to file
					outfile.write(
						user + ',' +
						str(datastore['id']) + ',' +
						str(rt) + ',' +
						str(date[0]) + ',' +
						str(date[1]) + ',' +
						str(date[2]) + ',' +
						str(datastore['created_at'])[11:19] + ',' +
						str(home) + ',' +
						str(coord[0]) + ',' + 
						str(coord[1]) + ',' +
						str(place)
					)
					outfile.write('\n')
				n_tweets_parsed += 1
				
				
			except Exception as e:
				logger.error(f"An exception occurred for tweet {n_tweets_parsed + 1}:\n {e}")
				continue
		logger.info(f"Parsed {n_tweets_parsed} tweets")
		logger.info(f"Parsed {n_users_parsed} users")