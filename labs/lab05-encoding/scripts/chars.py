import sys, unicodedata
data = open(sys.argv[1], 'rb').read()
for enc in ['cp1251', 'rk1048', 'pt154']: print('===', enc); print('\n'.join('U+%04X %s' % (ord(c), unicodedata.name(c,'?')) for c in sorted(set(data.decode(enc, errors='replace'))) if ord(c) > 127))
