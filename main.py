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
		#self.br = False
		self.data = []
		self.temp = []
		self.cell = ''

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
		#if self.recording and tag == 'br':
		#	self.br = True

	def handle_endtag(self, tag):
		if tag == 'table' and self.inTable:
			self.inTable = False
			return
		if tag == 'tr' and self.inLine:
			self.data.append(self.temp)
			self.temp = []
			self.inLine = False
			return
		if tag == 'td' and self.recording:
			self.temp.append(self.cell)
			self.cell = ''
			self.recording = False
			return

	def handle_data(self, data):
		if self.recording:
			#if not self.br:
			#	print(self.temp)
			#	self.temp.append(data)
			#elif len(self.temp) == 6:
			#	print(data)
			#	self.temp[-1] = self.temp[-1] + data
			#	self.br = False
			self.cell += data

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


#TODO
class Channel(namedtuple('Channel', 'chan, lang')):
	def __str__(self):
		return '{} [{}]'.format(self.chan, self.lang)

class Event(namedtuple('Event', 'time, sport, competition, event, live')):
	#__slots__ = ()
	def __str__(self):
		return ('Time: {}\n'
			'Sport: {}\n'
			'Competition: {}\n'
			'Event: {}\n'
			'Channels: {}\n').format(self.time, self.sport, self.competition, self.event, ', '.join(str(x) for x in self.live))
			#'Channels: {}',
			#'Language: {}'

def parse_raw_list(l):
	l = [[x.strip().replace('\\n\\t\\t', ' ') for x in y] for y in l]
	ret = []
	for i in l:
		#print(i)
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
			# quietly ignore
			#print('Error in line {}'.format(i))
			continue
		sport = i[2]
		competition = i[3]
		event = i[4]
		if '-' in event:
			event = event.split('-')
			event = (event[0], event[1])
		#print(i[5], 'END')
		
		i[5] = i[5].split()
		live = []
		for chans, lang in zip(i[5][0::2], i[5][1::2]):
			chans = (int(x) for x in chans.split('-') if x[0] != 'S')
			lang = lang[1:-1]
			for j in chans:
				live.append(Channel(j, lang))
			

		#DONETODO converto to namedtuple
		ret.append(Event(time, sport, competition, event, live))
	return ret

def get_link(ch):
	c = ch.chan
	req = urllib.request.Request('{}av{}'.format(site, c), headers={'User-Agent': 'Mozilla/5.0'})
	webpage = urllib.request.urlopen(req).read()        
	parser = LinksParser()
	parser.feed(str(webpage))
	return parser.url


if __name__ == '__main__':
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

	links_pro_benfiques = [get_link(y) for x in benfiques for y in x.live]

	for i in links_pro_benfiques:
		print(i)

	#urllib.request.urlopen(links_pro_benfiques[0][0])
		
## TODO
# ~Event pretty printing~
# Cleanup
# Cache stuff for performance
