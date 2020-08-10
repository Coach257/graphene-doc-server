import os
base_dir=os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(base_dir,'test.sqlite')
SQLALCHEMY_TRACK_MODIFICATIONS = False