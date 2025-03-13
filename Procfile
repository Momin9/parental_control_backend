release: python3 manage.py makemigrations && python3 manage.py migrate
web: gunicorn parental_control_backend.wsgi --timeout 60 --log-file -