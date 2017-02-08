import subprocess
#import xml.dom.minidom
import time

class LingPipe:
	path = ''
	def __init__(self, pathToLingPipe):
		self.path = pathToLingPipe
		self.process = subprocess.Popen([self.path],stdout=subprocess.PIPE,stdin=subprocess.PIPE)
	
	def parse(self, text):
		results = list()

		text = text.strip()
		if len(text) == 0:
			return results

		#print text
		#print str(self.process)
		for oneline in text.split('\n'):
			self.process.stdin.write(oneline+'\n')
			#print oneline
			while True:
				#print "HERE"
				r = self.process.stdout.readline()[:-1]
				#print r
				if not r:
					# Waiting for a blank line
					break
				results.append(r)
		return results

	def __del__(self):
		self.process.stdin.close()
		slippage = False
		for line in self.process.stdout:
			print "UNEXPECTED DATA:", line.strip()
			slippage = True
		if slippage:
			raise Exception('Lingpipe slippage occurred. Receiving additional Lingpipe data when none expected')
	
