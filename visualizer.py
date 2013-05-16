import sys
import re
from bs4 import BeautifulSoup
import urllib2
import operator

#sys.path.insert(0, '')
#global hashtable for storing the lanugage model
backgroundModel = {}

#initialize the language model
def init_lang():
	file = open('./wikiOccurance.txt', 'r')
	corpus = file.read().splitlines()
	file.close()
	for line in corpus:
		#get only the word part before the space
		word = line.split(' ')[0]
		#get the count and omit the newline character
		probability = line.split(' ')[1].split('\n')[0]
		#hash it so that a word maps to a count/probability
		#the first element of the hashtable will be the total number of words in the corpus
		backgroundModel[word] = probability

#parse the html text
def parser(text):
	#remove all non alphanumeric
	retval = re.sub('[^\w\s\']', ' ', text)
	#remove all whitespace
 	retval = re.sub('[\s]+', ' ', retval)
 	#replace newline characters
	retval = re.sub('\n', ' ', retval)
	#parsed result returned
	return retval

#produce a dictionary with each word mapping to its count/probability
def hash_the_shit(input):
	site_hash = {}
	for x in xrange(1,len(input[0])):
		if input[0][x] != '':
			if site_hash.get(input[0][x]) != None:
				site_hash[input[0][x]] += 1
			else:
				site_hash[input[0][x]] = 1
	return site_hash

#where all the magic starts
if __name__ == "__main__":
	#initialize the language model in the hashtable
	init_lang()
	#I guess headers are needed to spoof sources like wikipedia?
	req = urllib2.Request('http://en.wikipedia.org/wiki/Kevin_Durant', headers={'User-Agent' : "Magic Browser"}) 
	con = urllib2.urlopen(req)
	htmlsource = con.read()
	#make a beautifulsoup object
	soup = BeautifulSoup(htmlsource)
	#remove javascript stuff
	for s in soup('script'):
		s.extract()
	#store just the text, with no javascript
	text = soup.get_text().lower()
	#parse for whitespace, non-alphanumeric, etc. 
	output = parser(text.encode('utf-8'))		
	i = 0
	output = output.splitlines()
	output = [k.split(" ") for k in output]
	length = len(output[0])
	print length
	site_hash = hash_the_shit(output)	
	#we now have the hash of the site. We can compute language models
	#sort the dictionary in descending order
	sorted_hash = sorted(site_hash.iteritems(), key=operator.itemgetter(1), reverse=True)
	#we have an array of tuples. to access the word in the tuple we do sorted_hash[0][0]
	print sorted_hash

