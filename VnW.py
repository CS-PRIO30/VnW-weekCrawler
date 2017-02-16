# -*- coding: utf-8 -*-

#Author: CSPRIO30
#Email: cs.prio30@gmail.com
#Date: 2017/02/15
#Release-Notes: work with Visto-nel-Web v3

import json
from urlparse import urlparse 
import os
import textwrap
import cgi
import urllib
import glob
import shutil
import datetime
import os

#http://stackoverflow.com/questions/29358403/no-module-named-urllib-parse-how-should-i-install-it#29358613

'''
<p><strong>Why Has Cameroon Blocked the Internet?</strong><br />
quindi è fattibile di bloccare Internet e diffondere solo la verità (spesso post-) del Trump locale 😡<br />
<strong><span style="color:#808080;"><em>#:censura</em></span></strong><br />
::: <a href="https://yro.slashdot.org/story/17/02/08/1825242/why-has-cameroon-blocked-the-internet" target="_blank">Slashdot</a></p>

'''

CONFIG_TXT = "VnW_config.txt"
HOSTNAME_TXT = "Hostname.txt"
hostnameFileDict = {}
configFileDict = {}
folder = 0
#list starts with zero, months by 1,so "","01_Gennaio"...
monthlyFolders = ["","01_Gennaio","02_Febbraio","03_Marzo","04_Aprile","05_Maggio","06_Giugno","07_Luglio","08_Agosto","09_Settembre","10_Ottobre","11_Novembre","12_Dicembre"] 
lst = []	
notParsedFiles = []
allEntries = []
allEntriesTelegram = []
current_edition = ""
update_id = 0
allEntriesFavoritedTweets = []

def readCurrentEdition():
	global current_edition
	f = open(configFileDict["NAME_FILE_CURRENT_EDITION_VISTO_NEL_WEB"],"r")
	current_edition = int( f.read()) + 1 
	f.close()
	
def writeCurrentEdition():
	f = open(configFileDict["NAME_FILE_CURRENT_EDITION_VISTO_NEL_WEB"],"w")
	f.write(str(current_edition ))
	f.close()

def readConfigFile():
	global configFileDict
	global CONFIG_TXT
	f = open(CONFIG_TXT,"r")
	rows_config = f.read().split("\n")
	f.close()
	for row in rows_config:
		if row == "": # empty line
			pass
		else:
			if row[0] == "#": # it is a comment
				pass
			else:
				configFileDict[ row.split("=")[0].strip() ] = row.split("=")[1].strip()
		
def readHostnameFile():
	global HOSTNAME_TXT
	global hostnameFileDict
	f = open(HOSTNAME_TXT,"r")
	rows_hostFile = f.read().split("\n")
	f.close()
	for row in rows_hostFile:
		urlparse(row.split("\t")[0])
		hostname = urlparse(row.split("\t")[0]).netloc
		name_Declared_by_User = row.split("\t")[1]
		hostnameFileDict[ hostname ] =  name_Declared_by_User  #http://stackoverflow.com/questions/1024847/add-key-to-a-dictionary-in-python
		
def isTwitterUrl(url):
	return ("https://twitter.com/" in url and "/status/" in url)

def isYoutubeVideo(url):
	return ("youtube.com/" in url)

def getHostname(url):
	global hostnameFileDict
	#http://stackoverflow.com/questions/29358403/no-module-named-urllib-parse-how-should-i-install-it#29358613
	hostname = urlparse( url ).netloc
	#if twitter:
	# hostname is tweet's username, not url
	if isTwitterUrl(url):
		return url.split("https://twitter.com/")[1].split("/status/")[0]	
	if hostname in hostnameFileDict:
		return hostnameFileDict[hostname]
	#else...
	return hostname

def writeHtmlSpecialCharacters(string):
	#string = string.replace("€","&euro")
	string = string.replace("à","&agrave")
	string = string.replace("è","&egrave")
	string = string.replace("ì","&igrave")
	string = string.replace("ò","&ograve")
	string = string.replace("ù","&ugrave")
	string = string.replace("—","&#8211")
	string = string.replace("–","&#8211")
	return string

def getHtmlFromTwitter(url):
	#https://dev.twitter.com/rest/reference/get/statuses/oembed
	urlRequestTwitter = "https://publish.twitter.com/oembed?url=" + urllib.quote_plus( url.encode('utf-8') ) + "&maxwidth=" + configFileDict["WIDTH_PREVIEW_TWEET"] + "&lang=it"
	#print urlRequestTwitter
	jsonResponse = urllib.urlopen( urlRequestTwitter ).read()
	#print jsonResponse
	data = json.loads( jsonResponse )
	code = data["html"].replace("//platform.twitter.com/widgets.js","")
	code = code.replace("<script async src=\"\" charset=\"utf-8\"></script>","")
	code = code + ''' <script async src="http://platform.twitter.com/widgets.js" charset="utf-8"></script><br>'''
	return code

def removeDomainfromHostname(hostname):
	hostname = hostname.replace("www.","")
	hostname = hostname.replace(".com","")
	hostname = hostname.replace(".it","")
	hostname = hostname.replace(".net","")
	hostname = hostname.replace(".edu","")
	hostname = hostname.replace(".co.uk","")
	return hostname

def isImageUrl(url):
	global configFileDict
	imagesFormat = configFileDict["LIST_IMAGE_EXTENSION"].split(",")
	for item in imagesFormat:
		if ( item in url ):
			return True
	return False

def getHtmlCodeEntry(title = "", url = "", comment = "", hashtag = "", category = ""):
	global configFileDict
	str_twitter = ""
	line_break = "<br>"
	hostname = getHostname( url )
	
	hostname = removeDomainfromHostname(hostname)
	
	if ( hostname == "" ): 
		hostname = url
	
	if comment == "": # so that I don't write an unestethically empty line on the generated page
		comment_string = ""
	else:
		comment_string = comment + line_break
	
	if hashtag == "": # so that I don't write an unestethically empty line on the generated page
		hashtag_string = ""
	else:
		hashtagList = hashtag.split(",")
		newList = []
		for item in hashtagList:
			item.replace(" ","_")
			item = "#" + item.strip()
			newList.append(item)
		#print newList
		hashtag_string = ", ".join(newList)
		hashtag_string = hashtag_string + line_break
		
	#<IMMAGINE>
	if isImageUrl(url):
		#!!
		#http://stackoverflow.com/questions/3029422/how-do-i-auto-resize-an-image-to-fit-a-div-container
		#!!
		code = '''<a href="''' + url + '''">\n<img style="max-width:''' + configFileDict["MAX_WIDTH_IMAGE"] + ''';max-height:''' + configFileDict["MAX_HEIGHT_IMAGE"] + '''" width="auto" height="''' + configFileDict["HEIGHT_IMAGE"] +'''" src="''' + url + '''">\n</a>''' + line_break
		return code
	#</IMMAGINE>
	
	#<TWITTER>
	if ( isTwitterUrl(url) and configFileDict["ENABLE_TWEET_PREVIEW"] == "YES" ):
		code = getHtmlFromTwitter(url)
		return code
	if (isTwitterUrl(url) and configFileDict["ENABLE_TWEET_PREVIEW"] != "YES" ):
		title = title.split("\"")[1][0:-1]
		str_twitter = " " + str(configFileDict["STRING_TO_ADD_IF_URL_IS_TWITTER_TO_HOSTNAME"])
	#</TWITTER>
	
	if ( configFileDict["DO_I_HAVE_TO_LIMIT_MAX_SIZE_CHARACTERS_OF_TITLE"] == "YES" and len(title) > int(configFileDict["LIMIT_MAX_SIZE_CHARACTERS_OF_TITLE"]) ):
		width_size_wrap = int(configFileDict["LIMIT_MAX_SIZE_CHARACTERS_OF_TITLE"])
		placeholder = configFileDict["PLACEHOLDER_IN_CASE_OF_WRAP_YES"]
		title = textwrap.wrap(title, width = width_size_wrap, replace_whitespace=False)[0] + placeholder
	
	#<YOUTUBE>
	if ( isYoutubeVideo(url) ): #and configFileDict["ENABLE_YOUTUBE_EMBED"] == "YES" ):
		video_id = url.split("watch?v=")[1]
		aspect_ratio = 16.0/9
		code = '''  <iframe width="''' + str( aspect_ratio * int(configFileDict["MAX_HEIGHT_VIDEO"])) + '''" height="''' + configFileDict["MAX_HEIGHT_VIDEO"] +'''" src="https://www.youtube.com/embed/''' + video_id  +'''"></iframe>  '''
		return code
	#</YOUTUBE>
	
	code = '''<p><strong>''' + title + '''</strong>''' +  line_break + comment_string + '''<strong><span style=\"color:#808080;\"><em>''' + hashtag_string + '''</em></span></strong>''' +  ''':::''' + '''<a href="''' + url + '''" target="_blank">''' + hostname + str_twitter + '''</a></p>''' 
	return code

def orderChronologicallyList():
	a = []
	global lst
	if len(lst) == 0:
		return
	n = lst.index("Visto_nel_Web.txt")
	lst.pop(n) # if not following code fails
	for item in lst:
		number = item.split("(")[1].split(")")[0]
		a.append( int(number) ) 
	a.sort()
	del lst
	lst = []
	lst.append("Visto_nel_Web.txt")
	for i in range(len(a)):
		lst.append( "Visto_nel_Web(" + str( a[i] ) + ").txt" ) 

def makeDirectory(path): #http://stackoverflow.com/questions/600268/mkdir-p-functionality-in-python
	import errno    
	import os
	try:
		os.makedirs(path)
	except OSError as exc:  # Python >2.5
		if exc.errno == errno.EEXIST and os.path.isdir(path):
			pass
		else:
			raise

def crawlAndOrganize():
	global folder
	global notParsedFiles
	global monthlyFolders
	global lst
	global allEntries
	global current_edition
	now = datetime.datetime.now()
	currentYear = now.year
	currentMonth = now.month 
	'''
	lst = os.listdir(".")
	os.chdir( str(currentYear) )
	folder = folder + 1
	os.chdir( str(monthlyFolders[currentMonth]) )
	folder = folder + 1
	lst = os.listdir(".")
	lst = map(int, lst) #http://stackoverflow.com/questions/7368789/convert-all-strings-in-a-list-to-int
	os.chdir( str(lst[-1]) )
	folder = folder + 1
	print "Current directory is now: " + str( os.getcwd() )
	'''
	os.chdir( "current" )
	folder = folder + 1
	lst = os.listdir(".")
	
	orderChronologicallyList()
	
	print "Found " + str(len(lst)) + " files"
	print lst
	for filename in lst:
		try:
			print "\tProcessing " + str(filename)
			f = open(filename, "r")
			data = json.load(f)
			url = data["URL"]
			comment = data["COMMENT"]
			title = data["TITLE"]
			hashtag = data["HASHTAG"]
			category = data["CATEGORY"]
			allEntries.append( (title,url,comment,hashtag,category) )
			f.close()
		except: #http://stackoverflow.com/questions/4990718/python-about-catching-any-exception
			print "\t\tError parsing file."
			notParsedFiles.append(filename)
			#lst.pop( lst.index(filename) ) #remove not parsed file so list remain clean
			
	returnHome()

def returnHome():
	global folder
	for i in range(folder):
		os.chdir("..")
	folder = 0

def makeHtmlWebpage(allEntries):
	global folder
	global configFileDict
	string = ""
	n = len(allEntries)
	#print n
	f = open(configFileDict[ "NAME_FILE_OUTPUT" ] + "-" + str(current_edition) + "." + configFileDict[ "EXTENSION_FILE_OUTPUT_GENERATED" ].lower(),"a")
	for i in range(n):
		title = allEntries[i][0]
		url = allEntries[i][1]
		comment = allEntries[i][2]
		hashtag = allEntries[i][3]
		category = allEntries[i][4]
		f.write( getHtmlCodeEntry( title, url, comment,hashtag, category ).encode("utf-8") + "\n" )
	f.close()

def moveOldFiles():
	global current_edition
	global monthlyFolders
	now = datetime.datetime.now()
	currentYear = now.year
	currentMonth = now.month 
	dest_dir = "ARCHIVE/" + str(currentYear) + "/"  + monthlyFolders[currentMonth]  + "/" + "Visto-nel-Web--" + str(current_edition)
	makeDirectory( dest_dir )
	for filename in glob.glob( r'current/*.txt' ):
		shutil.move(filename, dest_dir)

def saveUrlsToFile():
	global configFileDict
	global allEntries
	if configFileDict["SAVE_ALL_URL_TO_A_FILE"] == "YES":
		f = open(configFileDict["NAME_FILE_SAVED_URL"],"a")
		for item in allEntries:
			f.write(item[1])
			f.write("\n")
		f.close()
		
def manageErrors(notParsedFiles):
	if len(notParsedFiles) > 0:
		print 
		print "File(s) not parsed: this output has also been written to '" + str(configFileDict["NAME_FILE_OUTPUT_IN_CASE_OF_ERROR"]) + "'"
		f = open(configFileDict["NAME_FILE_OUTPUT_IN_CASE_OF_ERROR"],"w")
		for item in notParsedFiles:
			print "\t" + item
			f.write( item + "\n")
		f.close()
		print

def getFavoritedTweets():
	print "(!)Start parsing favorited tweets" 
	global configFileDict
	global allEntriesFavoritedTweets
	from datetime import date, timedelta
	sevenDaysAgo = date.today() - timedelta(7)
	#print sevenDaysAgo
	import tweepy
	
	f = open("last_favorited_tweet.txt","r")
	lastFavoritedTweet = f.read()
	f.close()
	
	consumer_key = configFileDict["TWITTER_CONSUMER_KEY"]
	consumer_secret = configFileDict["TWITTER_CONSUMER_SECRET"]
	access_token = configFileDict["TWITTER_ACCESS_TOKEN"]
	access_token_secret = configFileDict["TWITTER_ACCESS_TOKEN_SECRET"]
	
	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	
	api = tweepy.API(auth)
	twHandle = configFileDict["USER_FAVORITED"]
	if twHandle[0] == "@":
		pass
	else:
		twhandle = "@" + twHandle
	tweetList = api.favorites( twhandle )
	for tweet in tweetList:
		twitterFavoritedUrl = "https://twitter.com/" + str(tweet.author.screen_name) + "/status/" +  str(tweet.id)
		if twitterFavoritedUrl == lastFavoritedTweet: #do not repeat yourself
			break
		else:
			print "\t" + str(twitterFavoritedUrl)
			url = twitterFavoritedUrl
			comment = ""
			text = ""
			hashtag = "twitter_favorites"
			category = "twitter-favorites"
			allEntriesFavoritedTweets.append( (text,url,comment,hashtag,category))
			
	f = open("last_favorited_tweet.txt","w")
	twitterFavoritedUrl = "https://twitter.com/" + str(tweetList[0].author.screen_name) + "/status/" +  str(tweetList[0].id)
	f.write( str( twitterFavoritedUrl ) )
	f.close()
	
	print "(!)Done parsing favorited tweets" 
	
def addTelegramEntries( bot ):
	global update_id
	global configFileDict
	global allEntriesTelegram
	print "(!)Processing Telegram messages..."
	for update in bot.getUpdates( offset=update_id, timeout=0.5 ):
		update_id = update.update_id + 1
		if ( update.message.text and "http" in update.message.text ):
			text = update.message.text.split("http")[0].replace("Popular post in HackerNews (with 200+ points)","").rstrip().lstrip()
			url = "http" + update.message.text.split("http")[1]
			comment = ""
			hashtag = "telegram"
			category = "READ IT LATER"
			allEntriesTelegram.append( (text,url,comment,hashtag,category) )
			print "\t" + text
			print "\t\t" + url 
	#following line is needed to update the update_id also on telegram server?
	#otherwise I will get same messages again and again
	bot.getUpdates( offset=update_id, timeout=0.1 )
	print "(!)Done parsing Telegram messages"
		
		
		
def main():
	global notParsedFiles
	global configFileDict
	global allEntries
	global allEntriesTelegram
	global current_edition
	global update_id
	global allEntriesFavoritedTweets
	global current_edition
	readConfigFile()
	readHostnameFile()
	readCurrentEdition()
	#print getHostname("http://jvns.ca/blog/2017/02/08/weird-unix-things-cd/")
	crawlAndOrganize()
	makeHtmlWebpage(allEntries)
	if ( configFileDict["ENABLE_TELEGRAM_BOT_COLLECTION"] == "YES" ):
		import telegram
		from telegram.error import NetworkError, Unauthorized
		bot = telegram.Bot( configFileDict["TELEGRAM_TOKEN"] )
		try:
			update_id = bot.getUpdates()[0].update_id
			print update_id
		except IndexError:
			update_id = None
		try:
			addTelegramEntries( bot )
		except Unauthorized:
			update_id += 1
			
		makeHtmlWebpage(allEntriesTelegram)
	if configFileDict["ENABLE_LIST_FAVORITED_TWEETS_OF_USER"] == "YES":
		getFavoritedTweets()
		makeHtmlWebpage(allEntriesFavoritedTweets)
	moveOldFiles()
	manageErrors( notParsedFiles )
	saveUrlsToFile()
	writeCurrentEdition()
	print "Output html code written to " + configFileDict[ "NAME_FILE_OUTPUT" ] + "-" + str(current_edition) + "." + configFileDict[ "EXTENSION_FILE_OUTPUT_GENERATED" ].lower()

main()