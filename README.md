sercomm
=======

A Python interface Sercomm IP camera configuration

Usage
-----

```python
from sercomm import SercommCamera
camera = SercommCamera('10.0.1.123', username='administrator', password='', ssl=False)

# Configure a POST webhook. Only a single webhook is supported
camera.enable_webhook('http://myserver/webhooks/webhook_id', method='POST')

# Enable events, triggered at most once per minute
camera.set_event_interval(enabled=True, interval=1)

# Enable webhook for passive infrared and video motion detection events
camera.set_event_destinations('pir', webhook=True)
camera.set_event_destinations('mt', webhook=True)

# Get the current MJPEG video address
print(camera.mjpeg_url)
```
