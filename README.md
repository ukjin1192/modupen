# django-modupen

- Source code of modupen service build with django


## What is moduepn?

- <a href="https://modupen.com" target="_blank">Modupen</a> is a platform for people to tmake story in relay


## What kinds of technologies inside?

- Based on Amazon Web Service for deployment
- Django 1.8.6 + Nginx + uWSGI
- MySQL + Redis
- Cloudinary for image processing
- Firebase for real-time database


## How can I customize?

~~~~
$ cd {PROJECT PATH}/conf
$ cp -R sensitive-data/ sensitive/
$ vi configuration.ini [Fill out variables]
$ vi newrelic.ini [Fill out license key]
$ vi remote_server.pem [Fill out public certificate of remote server]
~~~~
