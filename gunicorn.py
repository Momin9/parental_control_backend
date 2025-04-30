# gunicorn.py configuration example
bind = "127.0.0.1:8000"
workers = 3
timeout = 120
loglevel = 'info'
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
