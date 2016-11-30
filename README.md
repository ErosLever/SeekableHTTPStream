# SeekableHTTPStream

This is a generic wrapper for file-like objects that allows a stream opened with urllib.urlopen to support _seek_ and _tell_ operations.
This is implemented using the HTTP Range header, opening a new connection from the specified offset.
Differently from other implementations (e.g., https://github.com/valgur/pyhttpio) this module only opens a new connection if necessary, avoiding the generation of useless overhead (small seek forward or seek past the end of the file).

Example usage:
```
shs = SeekableHTTPStream("https://example.com/data.zip")
zz = zipfile.ZipFile(shs)
ff = zz.open("data/plugins.json")
data = json.load(ff)
```
