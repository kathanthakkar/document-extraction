# -*- coding: utf-8 -*-
"""
Created on Tue Jun  4 11:32:34 2019

@author: Anshul
"""

from flask import Flask
from flask_restplus import Api, Resource, fields

UPLOAD_FOLDER = r'C:\Users\Dell\Desktop\intern\document-extraction\pdfs'

app = Flask(__name__)
#api = Api(app)
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
