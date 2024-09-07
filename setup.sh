# Install dependency
pip install setuptools
pip install -r requirements.txt

#Run Django Command
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput