from html.parser import HTMLParser
import urllib.request
import datetime
from collections import namedtuple

class TableParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.inTable = False
		self.inLine = False
		self.recording = False
		self.data = []
		self.temp = []

	def handle_starttag(self, tag, attr):
		if (tag == 'table' and 
			('class', "auto-style1") in attr and 
			('style', "width: 100%; float: left") in attr and
			('cellspacing', "1") in attr and
			('align', "center") in attr):
			self.inTable = True
			return
		if self.inTable and tag == 'tr':
			self.inLine = True
			return
		if self.inLine and tag == 'td':
			self.recording = True

	def handle_endtag(self, tag):
		if tag == 'table' and self.inTable:
			self.inTable = False
			return
		if tag == 'tr' and self.inLine:
			#print(self.data)
			#print(self.temp)
			self.data.append(self.temp)
			self.temp = []
			#print(self.data)
			#print(self.temp)
			#print('-----')
			self.inLine = False
			return
		if tag == 'td' and self.recording:
			self.recording = False
			return

	def handle_data(self, data):
		if self.recording:
			self.temp.append(data)

class LinksParser(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.url = ''

	def handle_starttag(self, tag, attr):
		if tag == 'a':
			for i,j in attr:
				if i == 'href' and j.strip()[:12] == 'acestream://':
					self.url = j
					return

	def handle_endtag(self, tag):
		pass

	def handle_data(self, data):
		pass

#Event = namedtuple('Event', 'time, sport, competition, event, live_chan, live_lang')

class Channel(namedtuple('Channel', 'number, lang')):
	def __str__(self):
		return '{} [{}]'.format(no, lang)

class Event(namedtuple('Event', 'time, sport, competition, event, live_chan, live_lang')):
	#__slots__ = ()
	def __str__(self):
		return ('Time: {}\n'
			'Sport: {}\n'
			'Competition: {}\n'
			'Event: {}\n').format(self.time, self.sport, self.competition, self.event)
			#'Channels: {}',
			#'Language: {}'
		

def parse_raw_list(l):
	l = [[x.strip() for x in y] for y in l]
	ret = []
	for i in l:
		#print(len(i))
		if len(i) != 6:
			continue
		#day = [int(x) for x in i]
		#day = datetime.date(day[2], day[1], day[0])
		time = i[0]+' '+i[1]
		#couldn't get it to recognize CET so had to do this hack#
		time = time[:-3]+'+0100'
		try:
			time = datetime.datetime.strptime(time, '%d/%m/%Y %H:%M %z')# %Z')
		except ValueError:
			print('Error in line {}'.format(i))
			continue
		sport = i[2]
		competition = i[3]
		event = i[4]
		if '-' in event:
			event = event.split('-')
			event = (event[0], event[1])
		live_chan = i[5].split()[0]
		live_lang = i[5].split()[1]
		live_chan = tuple(int(x) for x in live_chan.split('-') if x[0] != 'S')
		live_lang = live_lang[1:-1]
		#DONETODO converto to namedtuple
		ret.append(Event(time, sport, competition, event, live_chan, live_lang))
	return ret

	#return [(datetime.date(x[0], x[1],) for x in l]

#with urllib.request.urlopen('http://arenavision.in/agenda/') as response:
#    html = response.read()
#    print(html)
	
	
site = 'http://arenavision.in/'

req = urllib.request.Request(site+'agenda', headers={'User-Agent': 'Mozilla/5.0'})
webpage = urllib.request.urlopen(req).read()
#print(webpage)

parser = TableParser()
parser.feed(str(webpage))

#for i in parser.data:
#    try:
#        print(i[0])
#    except IndexError:
#        pass
	
d = parse_raw_list(parser.data)

#for i in d:
#    print(i)

futebole = [x for x in d if x.sport == 'SOCCER']
benfiques = [x for x in d if 'BENFICA' in x.event]

#for i in futebole: print(i)
#print('---')
for i in benfiques: print(i)

def get_links(ev):
	ch = ev.live_chan
	#ch = [ for x in ch]
	ret = []
	for i in ch:
		req = urllib.request.Request('{}av{}'.format(site, i), headers={'User-Agent': 'Mozilla/5.0'})
		webpage = urllib.request.urlopen(req).read()        
		parser = LinksParser()
		parser.feed(str(webpage))
		ret.append(parser.url)
	return ret

links_pro_benfiques = [get_links(x) for x in benfiques]

for i in links_pro_benfiques:
	print(i)
	
## TODO
# Event pretty printing
# Cleanup
# Cache stuff for performance