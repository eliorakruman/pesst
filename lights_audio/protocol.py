
"""
Protocol:
CLIENT: 
- pause
- start <seconds> : Starts lights at time X with the light data previously uploaded. Seconds has max 3 decimal places. 
Uploading is done in 2 parts. A 'upload' message to give time for the server the delete the previous light data, which is responded by ok when ready, and then the file. 
- upload [File] : Uploads a file of light data. This should be used for all f. To save space, the previous light data may be deleted. 

SERVER:
Responds with 'ok' or 'er'
"""

"""
Light Data File format

SYNTAX
This is using Extended Backus Naur Form. All plain text is quoted with single quotes. A space does not mean theres actually a space unless its quoted!

<FILE>      = <header> '\n' <body>
<header>    = \\d+ '.' \\d{0,3}    # {0,3} may not be accurate, I forgot
<body>      = <line> '\n' | <body><body>
<line>      = \\d+ '.' \\d{0,3} ' ' <rgb> ' ' <rgb> ' ' <rgb>
<rgb>       = 0..255

HEADER DESCRIPTION:
The header contains the average BPM of the song rounded to 3 decimal places.

BODY DESCRIPTION:
Each line of the body contains a timestamp in seconds, rounded to maximum 3 decimal places, and 3 values from 0-255 representing RGB values.
"""

# Communication constants to be used by client and server
PAUSE = "pause"
START = "start"
UPLOAD = "upload"
DONE = "done"
OK = "ok"
ERR = "er"


class InvalidFormatError(RuntimeError):
    ...