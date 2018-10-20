# Python < 3
# see LICENSE file for licensing information

# Currently hardwired to compare Apple's "Programmer's Aid #1" binary
# image with binary code in the Mystery House ADVENTURE file.  See
# codediff.out for output.

# compare two chunks of binary code that should be almost identical

def dodiff(file1, off1, file2, off2, exceptions, skip):

	# read in binary file parts to compare - shorter file should be file1
	f = open(file1, 'rb')
	d1 = bytearray(f.read())
	f.close()

	f = open(file2, 'rb')
	d2 = bytearray(f.read())
	f.close()

	i1 = off1
	i2 = off2
	while i1 < len(d1):
		if d1[i1] == d2[i2]:
			# nothing to see here, move along
			i1 += 1
			i2 += 1
			continue

		# resync when needed
		if i1 in skip:
			resume = skip[i1]
			while d1[i1] != resume:
				print 'skip 1: %02x @ %04x' % (d1[i1], i1)
				i1 += 1
			while d2[i2] != resume:
				print 'skip 2: %02x @ %04x' % (d2[i2], i2)
				i2 += 1
			continue

		# exception check to filter slightly changed addrs, seems to
		# be high byte where we spot the difference
		w1 = (d1[i1] << 8) | d1[i1-1]
		w2 = (d2[i2] << 8) | d2[i2-1]
		print '%04x %04x' % (w1, w2)
		if w1 - 0xd000 + 0x6a00 == w2:
			i1 += 1
			i2 += 1
			continue
		if w1 in exceptions and exceptions[w1] == w2:
			i1 += 1
			i2 += 1
			continue

		print '%s @ 0x%04x = 0x%02x, %s @ 0x%04x = 0x%02x' % (
			file1, i1, d1[i1],
			file2, i2, d2[i2]
		)
		i1 += 1
		i2 += 1

if __name__ == '__main__':
	dodiff("APPLE II - 341-0016 - PROGRAMMER'S  AID #1 - 2716.bin", +0,
		'../disk/ADVENTURE', +0x6204,
		{
		},
		{
			0x0356:	0x8d,
			0x038a:	0xa8,
		})
