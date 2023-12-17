# PLANETARIUM API SERVICE

Django Rest project for social media api that allows user's to create profile, follow other user's, making posts and comments  

# Planetarium api service can be downloaded from
[Social media api from git hub](https://github.com/sasha-semenenko/social-media-api/tree/develop)

# Installation

```shell
git clone https://github.com/sasha-semenenko/social-media-api.git
cd social-media-api
python3 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Fill .env file with data according to .env_sample file

```shell
python manage.py migrate
python manage.py runserver 
```

* Create/get JWT-token and authorization
* Use social-media-api-application

# Project Schema
![Website Interface](static/images/social%20media%20api%20schema.jpg)

# Swagger schema endpoints
![Website Interface](static/images/social%20media%20api%20schema.jpg)
