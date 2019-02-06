# Image/video streams
PATH_IMAGE_SNAPSHOT = '/img/snapshot.cgi'
PATH_IMAGE_MJPEG = '/img/video.mjpeg'
PATH_IMAGE_RTSP = '/img/media.sav'

# PTZ Control
PATH_PAN_TILT = '/pt/ptctrl.cgi'
PARAM_PAN_TILT_DIRECTIONS = ('U', 'D', 'L', 'R', 'UL', 'UR', 'DL', 'DR')

# Configuration Groups
PATH_GET_GROUP = '/adm/get_group.cgi'
PATH_SET_GROUP = '/adm/set_group.cgi'

# System info
PATH_INFO_STATUS = '/util/query.cgi?extension=yes'
PATH_INFO_VERSIONS = '/adm/sysinfo.cgi'

# Telnetd backdoor
PATH_TELNETD = '/adm/file.cgi?todo=inject_telnetd'
USER_TELNETD = 'root'
PASS_TELNETD = 'Aq0+0009'

# Possible event triggers
EVENT_TRIGGERS = ['in1', 'in2', 'mt', 'pir', 'httpc', 'audio']
