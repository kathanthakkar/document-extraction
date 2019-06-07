# -*- coding: utf-8 -*-
"""
Created on Wed Jun  5 13:27:29 2019

@author: Anshul
"""

import os
from app import app
from flask import Flask, flash, request, redirect, render_template, url_for
from werkzeug.utils import secure_filename

filepath = ' '
keyword = ' '
ALLOWED_EXTENSIONS = set(['pdf'])

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
	
@app.route('/')
def upload_form():
	return render_template('upload.html')

@app.route('/', methods=['POST'])
def upload_file():    
    global filepath    
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected for uploading')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            filepath = 'pdfs/'+filename
            flash('File(s) successfully uploaded')
            return redirect(url_for('process_input'))

@app.route('/process', methods=['GET', 'POST'])
def process_input():
    return render_template('process.html')
'''
@app.route('/process', methods=['POST'])
def process_file():
    global keyword
    flash('Hello Admin')

    if request.method == 'POST':
      keyword = request.form['keyword']
      return 'Hello Admin'
      flash('Keyword Submitted')
      return redirect(url_for('result_display'))
'''
@app.route('/result_display', methods = ['POST', 'GET'])
def result_display():
    global keyword
    if request.method == 'POST':
      result = request.form['keyword']
      keyword = result
      return render_template("resultdisplay.html",result = result)

if __name__ == "__main__":
    app.run()