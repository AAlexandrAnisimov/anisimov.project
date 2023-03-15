import os

class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

DB_URI = "postgres://roucctioxhkyxi:c839849d5b249066257834b99a05b595ecd3b582bf4639eb8f112dd25abbe8f0@ec2-176-34-234-47.eu-west-1.compute.amazonaws.com:5432/d86qq8f0qif6v2"
