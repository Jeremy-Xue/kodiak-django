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
## Heroku Deployment
URL: `banana-tart-91724.herokuapp.com'
In order to make changes to heroku deployment, commit and push your changes to 
whichever branch you're working on, then run 
```bash
git push heroku master
```

Then you should be chillin.