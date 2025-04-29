import multiprocessing

bind = '0.0.0.0:8000'
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
errorlog = '/var/log/gunicorn/error.log'
accesslog = '/var/log/gunicorn/access.log'