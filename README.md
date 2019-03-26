# kodiak-django
Django backend for kodiak afterschool signup

## Initial Migrations
If this is your first time using the app, you have to run  `makemigrations` command in django.

In order to do this, make sure you're in the pipenv shell within the `kodiak_activity_backend` directory.

The `makemigrations` command's usage is as follows.
```bash
python manage.py makemigrations {app name}
```

For us, since our app name is `backend`, we run
```bash
python manage.py makemigrations backend
```
