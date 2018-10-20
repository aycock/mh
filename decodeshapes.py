# Python < 3
# see LICENSE file for licensing information

# Shape table reconstruction using turtle graphics based on info from the
# Applesoft BASIC Programming Reference Manual.

# Takes binary memory dump from emulator as input.  For Mystery House, dump
# $5700-$5a00 and $5500-$5700.

import sys
import turtle

DOTSIZE = 5

def plot(x):
	plot = x >> 2

	if plot:
		turtle.dot(DOTSIZE)

	dir = [ 90, 0, 270, 180 ][x & 3]
	turtle.setheading(dir)
	turtle.fd(DOTSIZE)

def shape(data):
	turtle.reset()
	turtle.ht()
	turtle.pu()
	turtle.tracer(0, 0)

	i = 0
	while True:
		byte = data[i]
		i += 1
		if byte == 0:
			break

		A = byte & 7
		B = (byte >> 3) & 7
		C = (byte >> 6) & 7

		plot(A)
		plot(B)
		if C != 0:
			plot(C)
	turtle.update()

def table(data):
	n = data[0]
	print n, 'shapes in shape table'

	for i in range(1, n+1):
		print 'shape definition', i
		index = (data[i * 2 + 1] << 8) | data[i * 2]
		shape(data[index:])
		raw_input()

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'usage: python', argv[0], '<memorydump.bin>'
		exit()

	f = open(sys.argv[1], 'rb')
	data = bytearray(f.read())
	f.close

	table(data)
