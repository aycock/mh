# Python < 3
# see LICENSE file for licensing information

# Renders all the images in one of Mystery House's BLOCK files using
# turtle graphics.

import sys
import turtle

def process(file):
	f = open(file)
	s = f.read()
	f.close()

	# print metadata
	print 'start address', hex(ord(s[1])*256 + ord(s[0]))
	n = ord(s[3])*256 + ord(s[2])
	print 'length', n, '=', hex(n)

	s = s[4:]
	turtle.ht()

	for i in range(0, n, 2):
		b1 = ord(s[i])
		b2 = ord(s[i+1])
		#print hex(b1), hex(b2)
		if b2 != 255:
			# if b1 is x-pos and b2 is y-pos, for hires+text
			# the resolution was 280x160
			assert b2 < 160
		print b1, b2
		if b1 == b2 == 0x00:
			turtle.pu()
		elif b1 == b2 == 0xff:
			raw_input()
			turtle.reset()
			turtle.ht()
		else:
			# apple's y=0 would've been at top of screen
			turtle.goto(b1, 280-b2)
			turtle.pd()

if __name__ == '__main__':
	if len(sys.argv) != 2:
		exit('usage: python %s BLOCK-file' % sys.argv[0])
	process(sys.argv[1])
		
