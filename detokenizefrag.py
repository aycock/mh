# Python < 3
# see LICENSE file for licensing information

# Partial detokenization of LISA assembler fragments found in a binary file.

import sys

TOKENS = {
	# reversed by comparing assembly fragments to Mystery House disasm
	# later verified against LISA decoder at
	# https://github.com/fadden/ciderpress/blob/master/reformat/Asm.cpp
	0xcb:	'jsr',
	0xca:	'jmp',
	0xac:	'tax',
	0xce:	'ldx',
	0xcd:	'lda',
	0xcf:	'ldy',
	0xd2:	'sty',
	0xd0:	'sta',
	0x96:	'brk',
	0xad:	'tay',
	0x99:	'clc',
	0xd1:	'stx',
	0xc0:	'adc',

	0xc4:	'cmp',		# very likely but not 100% sure about these
	0x86:	'bne',
	0x87:	'beq',

	# directives prepended with '.' to distinguish from assembly instrs
	# names updated per LISA decoder at
	# https://github.com/fadden/ciderpress/blob/master/reformat/Asm.cpp
	#0xd8:	'.dw',		# 2-byte word
	0xd8:	'.adr',		# 2-byte word
	#0xe4:	'.db',		# one or more hex bytes
	0xe4:	'.hex',		# one or more hex bytes
	0xdf:	'.asc',		# ASCII string, no terminator
}

def process():
	lines = disk.split(chr(0x0d))

	for line in lines:
		if len(line) == 0:
			# skip (XXX but can you have a line of length $d?)
			continue
		elif line[0] != len(line):
			if line[0] < len(line) and line[line[0]] == 0x20:
				# seems to happen with labels, kind of
				# a two-part line
				s = ''.join([ chr(b) for b in line[1:line[0]] ])
				print s
				line = line[line[0]+1:]
			else:
				# skip, probably corrupted or not part
				# of assembly fragment
				print '[...]'
				continue

		line = line[1:]		# lose length byte

		# opcode on line?
		if line[0] & 0x80:
			# opcode token and operand format byte
			if line[0] in TOKENS:
				print '\t' + TOKENS[line[0]],
			else:
				print '%02x %02x' % (line[0], line[1]),
			line = line[2:]

		# rest must be ASCII: operand, comment

		s = ''
		lastascii = True
		for b in line:
			if b >= ord(' ') and b < 127:
				s += chr(b)
				lastascii = True
			else:
				if lastascii == True and b & 0x80:
					# high bit seems to flag the
					# end of operand field when
					# inline comment follows
					s += chr(b & 0x7f)
					lastascii = True
				else:
					s += ' %02x ' % b
					lastascii = False
		print s

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'Usage" python', sys.argv[0], '<image.dsk>'
		exit()

	f = open(sys.argv[1], 'rb')
	disk = bytearray(f.read())
	f.close()

	process()
