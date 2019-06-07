# -*- coding: utf-8 -*-
"""
Created on Fri Jun  7 14:36:14 2019

@author: Anshul
"""

import os
#from app import app
from flask import Flask, flash, request, redirect, render_template, url_for, abort
from werkzeug.utils import secure_filename
import werkzeug
from flask_restplus import Api, Resource, fields, reqparse

app = Flask(__name__)
api = Api(app)
UPLOAD_FOLDER = 'G:\Internship\Main\Flask App\document-extraction\pdfs'
file_upload = reqparse.RequestParser()
file_upload.add_argument('pdf_file',  
                         type=werkzeug.datastructures.FileStorage, 
                         location='files', 
                         required=True, 
                         help='Upload a pdf file')

@api.route('/upload/')
class my_file_upload(Resource):
    @api.expect(file_upload)
    def post(self):
        args = file_upload.parse_args()
        if args['pdf_file'].mimetype == 'application/pdf':
            destination = UPLOAD_FOLDER
            if not os.path.exists(destination):
                os.makedirs(destination)
            xls_file = os.path.join(destination, 'custom_file_name.pdf')
            args['pdf_file'].save(xls_file)
        else:
            abort(404)
        return {'status': 'Done'}

if __name__ == "__main__":
    app.run()