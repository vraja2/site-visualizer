import sys
import re
from bs4 import BeautifulSoup
import urllib2
from urllib2 import urlopen
import operator
import cgi
from urllib2 import HTTPError
import requests
import contextlib
import lxml
import lxml.html as LH
import lxml.html.clean as clean
import json
import collections
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

def jsonify(sorted_tuples):
	json_list = []
	for x in xrange(1,20):
		json_list.append({'word': sorted_tuples[x][0], 'count': sorted_tuples[x][1]})
	return json_list

#where all the magic starts
if __name__ == "__main__":
	form = cgi.FieldStorage()
	form_content = form.getvalue('content')
	form_content = "http://www." + form_content
	#check formatting of the url
	if is_valid_url(form_content) == False:
		print "INVALID FORMAT"
	else:
		r = requests.head(form_content)
		#bad status (i.e 404, 500, etc.)
		if (r.status_code/100 >= 4):
			print "INVALID STATUS"
		else:
			#initialize the language model in the hashtable
			init_lang()
			#I guess headers are needed to spoof sources like wikipedia?
			req = urllib2.Request(form_content, headers={'User-Agent' : "Magic Browser"}) 
			con = urllib2.urlopen(req)
			htmlsource = con.read()
			#clean up the html to prevent bad start/end tags
			cleaner=clean.Cleaner()
    			htmlsource=cleaner.clean_html(htmlsource) 	
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
		        print ""
			#print length
			site_hash = hash_page(output)
			#we now have the hash of the site. We can compute language models
			#sort the dictionary in descending order
			sorted_hash = sorted(site_hash.iteritems(), key=operator.itemgetter(1), reverse=True)
			json_sorted = json.dumps(jsonify(sorted_hash))
			#print json_sorted
			#we have an array of tuples. to access the word in the tuple we do sorted_hash[0][0]
			RESULT_HTML = """\
			<html>
			<head>
			<style type ="text/css">
			div.bar {
				display: inline-block;
				width: 20px;
				height: 75px;
				background-color: teal;
				margin-right: 2px;
			}
			</style>
			</head>
			<body>
			<script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
			<script type="text/javascript">
			var test = %s
			var w = 1200;
			var h = 200;
			var y = d3.scale.linear()
				  .domain([0,test[0].count])
				  .range([0,h-15]);
			var svg = d3.select("body")
				    .append("svg")
				    .attr("width", w)
				    .attr("height", h);
			svg.selectAll("text")
			   .data(test)
			   .enter()
			   .append("text")
			   .text(function(d) { return d.word; })
			   .attr("x",  function(d,i) { return i * (w/test.length);})
			   .attr("y", function(d) { return h - y(d.count) -5; });
		           //.attr("text-anchor", "start");
			   //.attr("transform", function(d) {return "rotate(90)"; })
			 
			svg.selectAll("text")
			   .data(test)
			   .enter()
			   .append("text")
			   .text(function(d) { return d.count; })
			   .attr("x", function(d,i) { return i * (w/test.length);})
			   .attr("y", function(d) { return h - y(d.count) -5; });

		        svg.selectAll("rect")
			   .data(test) //import data
			   .enter() 
			   .append("rect") //create a rectangular svg
			   .attr("x", 0) 
			   .attr("width", 50) //width of each rect is 20px
			   .attr("y", function(d) { return h - y(d.count); })
			   .attr("height", function(d) { return y(d.count); })
			   .attr("x", function(d,i) { return i * (w/test.length); });
			</script>
			</body>
			</html>
			""" % json_sorted
			HOME_PAGE_HTML = """\
			<html>
		    	<body>
		        <form action="/run_script" method="post">
		            <br>Search Again!<br>
		            http://www.<input type="text" name="content" rows="3" cols="100">
		            <div><input type="submit" value="Visualize"/></div>
		        </form>
		    	</body>
			</html>
			"""
			print RESULT_HTML

