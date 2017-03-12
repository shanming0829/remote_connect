try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

io = StringIO()

io.write('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\nbbbbbbbbbbbbbbbbbbbbbb')
io.flush()
print io.getvalue()

io.seek(0)
io.write('ccc')
io.flush()
# io.reset()

print io.read()
print io.getvalue()
