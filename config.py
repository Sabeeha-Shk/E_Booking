import os

class Config:
    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:sql-404@localhost/e_booking'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
