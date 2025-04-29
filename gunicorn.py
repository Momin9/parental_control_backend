# gunicorn.py configuration
bind = 'unix:/home/ec2-user/parental_control_backend/parental_control_backend.sock'
workers = 3
worker_class = 'sync'
timeout = 120
accesslog = '/var/log/gunicorn/access.log'  # Ensure the access log path is correct
errorlog = '/var/log/gunicorn/error.log'  # Ensure the error log path is correct
