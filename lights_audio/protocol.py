"""
Protocol:
CLIENT: 
- pause
- start <seconds> : Starts lights at time X with the light data previously uploaded. Seconds has max 3 decimal places. 
- upload <bytes> : Uploading is done in 2 parts. 
1. A 'upload' containing the number of bytes is sent
2. Upon recieving ok from the client, the server sends over the file
- brighness percent : Sets brightness to percent

SERVER:
Responds with 'ok' or 'er'
"""

"""
Light Data File format

SYNTAX
This is using Extended Backus Naur Form. All plain text is quoted with single quotes. A space does not mean theres actually a space unless its quoted!

<FILE>      = <line>*
<line>      = <timestamp><color><color><color>
<color>     = 0..255 (1 byte)
<timestamp> = 0..65535 (2 bytes)


BODY DESCRIPTION:
Each line of the body contains a timestamp in seconds, and 3 values from 0-255 representing RGB values.
"""

# Communication constants to be used by client and server
PAUSE = "pause"
START = "start"
UPLOAD = "upload"
BRIGHTNESS = "brightness"
DONE = "done"
OK = "ok"
ERR = "er"

MIN_DIFF = 0.05 # Min difference between color time steps
SIG_FIGS = 100 # How much to multiply by to make above 1
DECIMAL_PLACES = 2
DEFAULT_BRIGHTNESS = 40

class InvalidFormatError(RuntimeError):
    ...

def decode_file(p: str):
    from pprint import pprint
    t: dict[float, tuple[int, int, int]] = {}
    with open(p, "rb") as f:
        b: bytes = f.read()
        r = 0
        while r < len(b):
            timestamp = int.from_bytes([b[r], b[r+1]], "big") / SIG_FIGS
            t[timestamp] = (b[r+2], b[r+3], b[r+4])
            r+=5
    pprint(t)

if __name__ == '__main__':
    decode_file("./client/songs/DISCO LINES - BABY GIRL [Lxu_9m23qHg].mp3.color")