#
# Constants specific to videos
#
# Thane
# 

# Regular expressions for parsing embed code
# YouTube embeds
YOUTUBE_FULL_REGEX       = r'\s*<object\s+width="(?P<width1>\d+)"\s+height="(?P<height1>\d+)">\s*<param\s+name="movie"\s+value="(?P<url1>(?P<protocol1>(http|https))://(?P<subdomain1>[a-z]+)\.youtube\.(?P<domain1>[a-z]+)/v/(?P<videocode1>[a-zA-Z0-9]*)[a-zA-Z0-9&=_]*)">\s*</param>\s*<param\s+name="allowFullScreen"\s+value="true">\s*</param>\s*<param\s+name="allowscriptaccess"\s+value="always">\s*</param>\s*<embed\s+src="(?P<url2>(?P<protocol2>(http|https))://(?P<subdomain2>[a-z]+)\.youtube\.(?P<domain2>[a-z]+)/v/(?P<videocode2>[a-zA-Z0-9]*)[a-zA-Z0-9&=_]*)"\s+type="application/x-shockwave-flash"\s+allowscriptaccess="always"\s+allowfullscreen="true"\s+width="(?P<width2>\d+)"\s+height="(?P<height2>\d+)">\s*</embed>\s*</object>\s*'
YOUTUBE_PARTIAL_REGEX    = r'\s*(?P<protocol>(http|https))://(?P<subdomain>[a-zA-Z0-9\.]*)\.youtube\.(?P<domain>[a-z]+)/watch\?v=(?P<videolink>[a-zA-Z0-9&=_]*)\s*'
# Zoopy embeds
ZOOPY_FULL_REGEX         = r'\s*<object\s+classid="clsid:(?P<clsid>[a-zA-Z0-9-]*)"\s+codebase="http://macromedia.com/cabs/swflash.cab#version=(?P<flashversion>[0-9,]*)"\s+id="zoopy-video-(?P<zoopyid1>\d+)"\s+width="(?P<width1>\d+)"\s+height="(?P<height1>\d+)">\s*<param\s+name="movie"\s+value="http://media.z2.zoopy.com/video-offsite.swf"\s*/>\s*<param\s+name="flashvars"\s+value="id=(?P<zoopyid2>\d+)"\s*/>\s*<param\s+name="quality"\s+value="high"\s*/>\s*<param\s+name="bgcolor"\s+value="#(?P<bgcolor1>\d+)"\s*/>\s*<param\s+name="allowscriptaccess"\s+value="always"\s*/>\s*<param\s+name="allowfullscreen"\s+value="true"\s*/>\s*<param\s+name="wmode"\s+value="opaque"\s*/>\s*<embed\s+src="http://media.z2.zoopy.com/video-offsite.swf"\s+allowfullscreen="true"\s+flashvars="id=(?P<zoopyid3>\d+)"\s+bgcolor="#(?P<bgcolor2>\d+)"\s+width="(?P<width2>\d+)"\s+height="(?P<height2>\d+)"\s+type="application/x-shockwave-flash"\s+allowscriptaccess="always"\s+wmode="opaque">\s*</embed>\s*</object>\s*'

# full embed codes
YOUTUBE_EMBED_CODE       = '<object width="%(width)s" height="%(height)s"><param name="movie" value="%(protocol)s://%(subdomain)s.youtube.%(domain)s/v/%(videolink)s&hl=en_US&fs=1&"></param><param name="allowFullScreen" value="true"></param><param name="allowscriptaccess" value="always"></param><embed src="%(protocol)s://%(subdomain)s.youtube.%(domain)s/v/%(videolink)s&hl=en_US&fs=1&" type="application/x-shockwave-flash" allowscriptaccess="always" allowfullscreen="true" width="%(width)s" height="%(height)s"></embed></object>'
ZOOPY_EMBED_CODE         = '<object classid="clsid:%(clsid)s" codebase="http://macromedia.com/cabs/swflash.cab#version=%(flashversion)s" id="zoopy-video-%(zoopyid)s" width="%(width)s" height="%(height)s"><param name="movie" value="http://media.z2.zoopy.com/video-offsite.swf" /><param name="flashvars" value="id=%(zoopyid)s" /><param name="quality" value="high" /><param name="bgcolor" value="#%(bgcolor)s" /><param name="allowscriptaccess" value="always" /><param name="allowfullscreen" value="true" /><param name="wmode" value="opaque" /><embed src="http://media.z2.zoopy.com/video-offsite.swf" allowfullscreen="true" flashvars="id=%(zoopyid)s" bgcolor="#%(bgcolor)s" width="%(width)s" height="%(height)s" type="application/x-shockwave-flash" allowscriptaccess="always" wmode="opaque"></embed></object>'
ZOOPY_DEFAULT_EMBED_CODE = '<object classid="clsid:d27cdb6e-ae6d-11cf-96b8-444553540000" codebase="http://macromedia.com/cabs/swflash.cab#version=9,0,0,246" id="zoopy-video-%(zoopyid)s" width="%(width)s" height="%(height)s"><param name="movie" value="http://media.z2.zoopy.com/video-offsite.swf" /><param name="flashvars" value="id=%(zoopyid)s" /><param name="quality" value="high" /><param name="bgcolor" value="#000000" /><param name="allowscriptaccess" value="always" /><param name="allowfullscreen" value="true" /><param name="wmode" value="opaque" /><embed src="http://media.z2.zoopy.com/video-offsite.swf" allowfullscreen="true" flashvars="id=%(zoopyid)s" bgcolor="#000000" width="%(width)s" height="%(height)s" type="application/x-shockwave-flash" allowscriptaccess="always" wmode="opaque"></embed></object>'

# default video width and height
DEFAULT_VIDEO_WIDTH      = 600
DEFAULT_VIDEO_HEIGHT     = 480

VIDEO_TIMESTAMP_FORMAT   = "%Y-%m-%dT%H:%M:%S+02:00"
