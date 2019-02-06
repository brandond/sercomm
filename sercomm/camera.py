"""
Basic support for interacting with Sercomm IP cameras from Python

All documentation sourced from: https://github.com/edent/Sercomm-API
"""

import requests
from . import const


class SercommError(Exception):
    pass


class SercommCamera(object):
    def __init__(self, host, port=80, username='administrator', password='', ssl=False):
        self.host = host
        self.port = port
        self.ssl = ssl
        self.session = requests.Session()
        self.session.auth = (username, password)

        if port == 443 and not ssl:
            self.ssl = True

    def format_uri(self, relative_path):
        proto = 'https' if self.ssl else 'http'
        return '{}://{}:{}{}'.format(proto, self.host, self.port, relative_path)

    def get(self, path, *args, **kwargs):
        url = self.format_uri(path)
        return self.session.get(url, *args, **kwargs)

    def post(self, path, *args, **kwargs):
        url = self.format_uri(path)
        return self.session.post(url, *args, **kwargs)

    def list_groups(self):
        response = self.get(const.PATH_GET_GROUP)
        return [l[1:-1] for l in response.text.splitlines()]

    def get_group(self, group):
        response = self.get(const.PATH_GET_GROUP, params={'group': group})
        return dict(l.split('=', 1) for l in response.text.splitlines() if not l.startswith('['))

    def set_group(self, group, **kwargs):
        kwargs['group'] = group
        return self.get(const.PATH_SET_GROUP, params=kwargs)

    def get_webhook(self):
        params = self.get_group('HTTP_NOTIFY')
        return {'enabled': params.get('http_notify') == '1',
                'url': params.get('http_url'),
                'username': params.get('http_user'),
                'password': params.get('http_passsword'),
                'method': 'GET' if params.get('http_method') == 0 else 'POST',
                }

    def enable_webhook(self, url, username='', password='', method='GET'):
        method = '0' if method.upper() == 'GET' else '1'
        response = self.set_group('HTTP_NOTIFY',
                                  http_notify=1,
                                  http_url=url,
                                  http_proxy='',
                                  http_proxy_no=80,
                                  http_method=method,
                                  http_user=username,
                                  http_password=password,
                                  event_data_flag=1)
        response.raise_for_status()

    def disable_webhook(self):
        response = self.set_group('HTTP_NOTIFY',
                                  http_notify=0,
                                  http_url='',
                                  http_proxy='',
                                  http_proxy_no=80,
                                  http_method=0,
                                  http_user='',
                                  http_password='',
                                  event_data_flag=0)
        response.raise_for_status()

    def get_http_upload(self):
        params = self.get_group('HTTP_EVENT')
        return {'enabled': params.get('http_post_en') == '1',
                'url': params.get('http_post_url'),
                'username': params.get('http_post_user'),
                'password': params.get('http_post_pass'),
                }

    def enable_http_upload(self, url, username='', password=''):
        response = self.set_group('HTTP_EVENT',
                                  http_event_en=1,
                                  http_post_en=1,
                                  http_post_user=username,
                                  http_post_pass=password,
                                  http_post_url=url)
        response.raise_for_status()

    def disable_http_upload(self):
        response = self.set_group('HTTP_EVENT',
                                  http_event_en=0,
                                  http_post_en=0,
                                  http_post_user='',
                                  http_post_pass='',
                                  http_post_url='')
        response.raise_for_status()

    def get_event_interval(self):
        params = self.get_group('EVENT')
        return {'enabled': params.get('event_trigger') == '1',
                'interval': params.get('event_interval'),
                }

    def set_event_interval(self, enabled, interval):
        enabled = '1' if enabled else '0'
        response = self.set_group('EVENT',
                                  event_trigger=enabled,
                                  event_interval=interval)
        response.raise_for_status()

    def get_event_destination(self, trigger):
        """Get destination configuration for a specific trigger."""
        if trigger not in const.EVENT_TRIGGERS:
            raise SercommError('Invalid event trigger - must be one of {}'.format(
                const.EVENT_TRIGGERS))
        params = self.get_group('EVENT')
        email, ftp, _, _, webhook, http_upload, _, _ = params.get('event_' + trigger, '0,0,0,0,0,0,0,0').split(',')
        return {'email': email == '1',
                'ftp': email == '1',
                'webhook': webhook == '1',
                'http_upload': http_upload == '1',
                }

    def set_event_destinations(self, trigger, **kwargs):
        """
        Enable or disable individual event destinations for a specific trigger.
        Destinations not specified will not be changed
        """
        if trigger not in const.EVENT_TRIGGERS:
            raise SercommError('Invalid event trigger - must be one of {}'.format(
                const.EVENT_TRIGGERS))

        destinations = self.get_event_destinations(trigger)
        for dest in destinations.keys():
            if dest in kwargs:
                destinations[dest] = '1' if bool(kwargs[dest]) else '0'

        destination_list = '{},{},0,0,{},{},0,0'.format(destinations['email'],
                                                        destinations['ftp'],
                                                        destinations['webhook'],
                                                        destinations['http_upload'])
        kwargs = {'event_' + trigger: destination_list}
        self.set_group('EVENT', **kwargs)

    def get_event_duration(self):
        """Get guality and duration (before and after) in seconds for event-triggered recordings"""
        params = self.get_group('EVENT')
        _, quality, before, after = params.get('event_attach', 'avi,3,1,1').split(',')
        return {'quality': quality,
                'before': before,
                'after': after,
                }

    def set_event_duration(self, quality, before, after):
        """Set guality and duration (before and after) in seconds for event-triggered recordings"""
        response = self.set_group('EVENT', event_attach='avi,{},{},{}'.format(quality, before, after))
        response.raise_for_status()

    def inject_telnetd(self):
        return self.get(const.PATH_TELNETD)

    @property
    def image_url(self):
        return self.format_uri(const.PATH_IMAGE_SNAPSHOT)

    @property
    def mjpeg_url(self):
        return self.format_uri(const.PATH_IMAGE_MJPEG)
