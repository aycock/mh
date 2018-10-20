# Python < 3
# see LICENSE file for licensing information

# Uses 64K binary memory dump from emulator as input, grabbed when $5e03 first
# hit in the game, along with Mystery House's MESSAGES file.  See dumpgame.out
# for output.

FILE = 'mh@5e03.bin'
MESSFILE = 'MESSAGES'

def dumpdict(label, addr):
	rv = {}
	print label
	n = 0
	while True:
		n += 1
		word = M[addr:addr+8]
		# strip high bit the Apple II so loved for ASCII chars
		word = ''.join([ chr(ord(ch) & 0x7f) for ch in word ])
		addr += 8
		print '#%d\t"%s"' % (n, word)
		rv[n] = word.strip()
		
		nsyn = ord(M[addr])
		if nsyn == 0xff:
			# end-of-dictionary sentinel
			break
		addr += 1

		# handle synonyms, if any
		while nsyn > 0:
			word = M[addr:addr+8]
			# strip high bit
			word = ''.join([ chr(ord(ch) & 0x7f) for ch in word ])
			addr += 8
			print '\t= "%s"' % word
			nsyn -= 1
	return rv

def dumpmess():
	print 'MESSAGES'
	messages = {}

	f = open(MESSFILE, 'rb')
	s = f.read()
	f.close()

	# message index is at $5500 in memory, also in "MESSAGE OBJECT" file
	n = 1
	while True:
		offset = ord(M[0x5500+n*2+1]) << 8
		offset |= ord(M[0x5500+n*2])
		if offset > len(s):
			break
		endpos = s.find(chr(0x8d), offset)	# find the <cr>
		mesg = s[offset:endpos+1]
		mesg = ''.join([ chr(ord(ch) & 0x7f) for ch in mesg ])
		mesg = mesg.strip()			# and strip the <cr>
		messages[n] = mesg
		print '#%d\t"%s"' % (n, mesg)
		n += 1
	return messages

def dumpobjects():
	print 'OBJECTS'
	objects = {}

	i = 0x900
	while True:
		objno = ord(M[i])
		if objno == 0xff:
			break
		objnoun = ord(M[i+1])
		objloc = ord(M[i+2])
		objpic = ord(M[i+3])
		objx = ord(M[i+5])
		objy = ord(M[i+6])
		objmesg = ord(M[i+8])
		objnext = ord(M[i+9])
		print '#%d\t%s at location %d, (x,y) = (%d,%d), picture %d' % (
			objno, nouns[objnoun], objloc, objx, objy, objpic
		)
		if objmesg != 0:
			print '\t"%s"' % messages[objmesg]
		objects[objno] = nouns[objnoun]
		i += objnext
	return objects

def dumprooms():
	print 'ROOMS'

	n = 0
	i = 0xd00
	while True:
		roommesg = ord(M[i+1])
		if roommesg not in messages:
			print '#%d\t???' % n
		else:
			print '#%d\t"%s"' % (n, messages[roommesg])
		dirs = ''
		if ord(M[i+2]) != 0:	dirs += 'N %d ' % ord(M[i+2])
		if ord(M[i+3]) != 0:	dirs += 'S %d ' % ord(M[i+3])
		if ord(M[i+4]) != 0:	dirs += 'E %d ' % ord(M[i+4])
		if ord(M[i+5]) != 0:	dirs += 'W %d ' % ord(M[i+5])
		if ord(M[i+6]) != 0:	dirs += 'U %d ' % ord(M[i+6])
		if ord(M[i+7]) != 0:	dirs += 'D %d ' % ord(M[i+7])
		if dirs != '':
			print '\t%s' % dirs
		print '\tpicture =', ord(M[i+8])
		i += 10
		n += 1
		if n == 42:
			# empirically determined
			break

def dumpcode(label, addr):
	print label

	while True:
		roomno = ord(M[addr])
		if roomno == 0xff:
			break
		verbno = ord(M[addr+1])
		nounno = ord(M[addr+2])
		next = ord(M[addr+3])
		nconds = ord(M[addr+4])
		ninstrs = ord(M[addr+5])

		L = []
		if roomno != 0xfe:
			L.append( 'ROOM = %d' % roomno )
		if verbno != 0xfe:
			L.append( 'VERB = "%s"' % verbs[verbno] )
		if nounno != 0xfe:
			L.append( 'NOUN = "%s"' % nouns[nounno] )

		pc = addr + 6
		for i in range(nconds):
			op = ord(M[pc])
			nargs = 0
			if op == 3:
				nargs = 2
				objno = ord(M[pc+1])
				loc = ord(M[pc+2])
				s = 'OBJECT "%s" ' % objects[objno]
				if loc == 0xfe:
					s += 'CARRIED'
				else:
					s += 'IN ROOM %d' % loc
			elif op == 5:
				nargs = 1
				s = 'TURN >= %d' % ord(M[pc+1])
			elif op == 6:
				nargs = 2
				varno = ord(M[pc+1])
				const = ord(M[pc+2])
				s = 'VAR %d = %d' % (varno, const)
			elif op == 9:
				nargs = 1
				const = ord(M[pc+1])
				s = 'CURPIC = %d' % const
			elif op == 10:
				nargs = 2
				objno = ord(M[pc+1])
				const = ord(M[pc+2])
				s = 'OBJECT "%s" PICTURE = %d' % (
					objects[objno],
					const
				)
			else:
				assert 0

			L.append(s)
			pc += 1 + nargs

		if len(L) == 0:
			conds = 'true'
		else:
			conds = ' and '.join(L)

		print 'if', conds, 'then'

		INSTRS = {
			1:	( 2, None ),
			2:	( 2, None ),
			3:	( 2, None ),
			4:	( 0, 'inventory' ),
			5:	( 2, None ),
			6:	( 1, None ),
			7:	( 1, None ),
			8:	( 1, None ),
			9:	( 1, None ),
			10:	( 0, 'normal image' ),
			11:	( 0, 'blank image' ),
			12:	( 0, 'brk @ 0x66a8' ),
			13:	( 0, 'exit to BASIC' ),
			14:	( 0, 'brk @ 0x66b1' ),
			15:	( 0, 'save game' ),
			16:	( 0, 'load game' ),
			17:	( 0, 'replay game' ),
			18:	( 4, None ),
			19:	( 2, None ),
			20:	( 0, 'restore room view' ),
			21:	( 0, 'go north' ),
			22:	( 0, 'go south' ),
			23:	( 0, 'go east' ),
			24:	( 0, 'go west' ),
			25:	( 0, 'go up' ),
			26:	( 0, 'go down' ),
			27:	( 0, 'take (NOUN)' ),
			28:	( 0, 'drop (NOUN)' ),
			29:	( 2, None ),
		}
		for i in range(ninstrs):
			op = ord(M[pc])
			if op not in INSTRS:
				print '\tunimp (%d)' % op
				continue

			nargs = INSTRS[op][0]
			argv = []
			for j in range(nargs):
				argv.append( ord(M[pc+j+1]) )

			if type(INSTRS[op][1]) == type(''):
				s = INSTRS[op][1]
			elif op == 1:
				s = 'VAR %d += %d' % (argv[1], argv[0])
			elif op == 2:
				s = 'VAR %d -= %d' % (argv[1], argv[0])
			elif op == 3:
				s = 'VAR %d = %d' % (argv[0], argv[1])
			elif op == 5:
				if argv[1] == 0xfe:
					s = 'carry object %s (%d)' % (
						objects[argv[0]], argv[0]
					)
				else:
					s = 'object %s (%d) location = %d' % (
						objects[argv[0]],
						argv[0], argv[1]
					)
			elif op == 6:
				s = 'goto room %d' % argv[0]
			elif op == 7:
				s = 'set temp room view to %d' % argv[0]
			elif op == 8:
				s = 'set room images to %d' % argv[0]
			elif op == 9:
				s = 'print "%s"' % messages[argv[0]]
			elif op == 18:
				s = 'object %s (%d) location = %d, (x,y) = (%d,%d)' % (
					objects[argv[0]], argv[0],
					argv[1],
					argv[2], argv[3]
				)
			elif op == 19:
				s = 'object %s picture = %d' % (
					objects[argv[1]], argv[0]
				)
			elif op == 29:
				s = 'set room %d images to %d' % (
					argv[0], argv[1]
				)
			else:
				assert 0

			print '\t%s' % s
			pc += 1 + nargs

		addr += next

f = open(FILE, 'rb')
M = f.read()
f.close

assert len(M) == 65536

# addresses from reversing
verbs = dumpdict('VERBS', 0x4000)
nouns = dumpdict('NOUNS', 0x1700)

messages = dumpmess()
objects = dumpobjects()
dumprooms()

dumpcode('HIGHPRI', 0x4500)
dumpcode('LOWPRI', 0x4400)
