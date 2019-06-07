# -*- coding: utf-8 -*-
"""
Created on Thu Jun  6 15:05:38 2019

@author: yashv
"""
from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
   name="abc"
   return render_template('index.html', name1=name)

if __name__ == '__main__':
   #app.debug = True
   app.run()

