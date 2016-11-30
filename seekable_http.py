import urllib2
from StringIO import StringIO

class SeekableHTTPStream(object):

	def __init__(self, url, max_skippable_bytes=512*1024):
		self.handle = urllib2.urlopen(url)
		self.url = self.handle.geturl()
		self.max_skippable_bytes = max_skippable_bytes
		self.offset = 0
		self.filesize = int(self.handle.info().getheader('Content-Length'))
		for func_name in ("readline","readlines","close"):
			setattr(self,func_name,getattr(self.handle,func_name))

	def read(self,*args,**kwargs):
		ret = self.handle.read(*args,**kwargs)
		if ret:
			self.offset += len(ret)
		return ret

	def tell(self):
		return self.offset

	def seek(self,offset,whence=0):
		if whence == 0: #from start
			target_offset = offset
		elif whence == 1: #from current
			target_offset = self.offset + offset
		elif whence == 2: # from end
			target_offset = self.filesize + offset
		else:
			target_offset = None
			raise ValueError()

		if target_offset >= self.filesize:
			target_offset = self.filesize
			self.handle.close()
			self.handle = StringIO()
		elif target_offset > self.offset and target_offset - self.offset <= self.max_skippable_bytes:
			#print "seek via read"
			self.handle.read(target_offset - self.offset)
		else:
			request = urllib2.Request(self.url)
			request.headers['Range'] = "bytes=%s-" % target_offset
			#print request.headers['Range']
			self.handle.close()
			self.handle = urllib2.urlopen(request)
			return_range = self.handle.headers.get('Content-Range')
			#print return_range
			if return_range != "bytes %d-%d/%s" % (target_offset, self.filesize-1, self.filesize):
				raise Exception("Ranged requests are not supported for this URI")
		self.offset = target_offset

if __name__ == "__main__":
	#"""
	"""
	shs = SeekableHTTPStream("https://github.com/wpscanteam/wpscan/raw/master/data.zip",0)
	a = shs.read(512) # pos: 0 -> 512
	b = shs.read(512) # pos: 512 -> 1024
	c = shs.read(512) # pos: 1024 -> 1536
	shs.seek(1024)	# pos: 1024
	d = shs.read(512) # pos: 1024 -> 1536
	print "c==d",c==d
	shs.seek(-1024,1) # pos: 512
	e = shs.read(512) # pos: 512 -> 1024
	print "e==b",e==b
	shs.seek(0)
	shs.max_skippable_bytes = 1024
	shs.seek(512)
	f = shs.read(512) # pos: 512 -> 1024
	print "e==f",e==f
	"""
	shs = SeekableHTTPStream("https://github.com/wpscanteam/wpscan/raw/master/data.zip")
	import zipfile
	zz = zipfile.ZipFile(shs)
	ff = zz.open("data/plugins.json")
	import json
	jj = json.load(ff)
	#"""
