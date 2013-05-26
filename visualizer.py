import sys
import re
from bs4 import BeautifulSoup
import urllib2
from urllib2 import urlopen
import operator
import cgi
from urllib2 import HTTPError
import requests

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
def hash_page(input):
	site_hash = {}
	for x in xrange(1,len(input[0])):
		if input[0][x] != '':
			if site_hash.get(input[0][x]) != None:
				site_hash[input[0][x]] += 1
			else:
				site_hash[input[0][x]] = 1
	return site_hash

#check if an input url is valid
def is_valid_url(url):
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url) is not None

#where all the magic starts
if __name__ == "__main__":
	form = cgi.FieldStorage()
	form_content = form.getvalue('content')
	if is_valid_url(form_content) == False:
		print "INVALID URL1"
	else:
		r = requests.head(form_content)
		if (r.status_code/100 >= 4):
			print "INVALID URL"
		else:
			#initialize the language model in the hashtable
			init_lang()
			#I guess headers are needed to spoof sources like wikipedia?
			req = urllib2.Request(form_content, headers={'User-Agent' : "Magic Browser"}) 
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
			site_hash = hash_page(output)	
			#we now have the hash of the site. We can compute language models
			#sort the dictionary in descending order
			sorted_hash = sorted(site_hash.iteritems(), key=operator.itemgetter(1), reverse=True)
			#we have an array of tuples. to access the word in the tuple we do sorted_hash[0][0]
			print sorted_hash

			HOME_PAGE_HTML = """\
			<html>
			    <body>
			        <form action="/run_script" method="post">
			            <div><textarea name="content" rows="3" cols="100"></textarea></div>
			            <div><input type="submit" value="Visualize"/></div>
			        </form>
			    </body>
			</html>
			"""
			print HOME_PAGE_HTML


