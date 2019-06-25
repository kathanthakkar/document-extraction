# Document-Extraction

This repo aims to create a web application/api which helps in extracting various information from scanned documents(mainly invoices) and present in a user-friendly manner.
The available formats by this code include xlsx and Json.
The code runs in Python Language making the use of :
     Flask-Restplus for API, 
     SQLAlchemy and MySQL for Database Management System.
     
The finished product : An API with 6 endpoints allowing uploading of file, adding and searching keywords along with other extra functions.
                       Presenting data in a created Excel file and Json format.
                       Extracting necessary information like number of pages, accuracy based on found keywords etc.
                       
Pre-requisites for the code
Installment requirements :

The code uses Python Language and we used Spyder tool in Anaconda Navigator. Start by installing Anaconda Navigator.
https://www.anaconda.com/distribution/

-- Provide paths of all the installed application by setting the environment variables --

Tesseract-OCR Application
https://github.com/UB-Mannheim/tesseract/wiki

ImageMagick Application
https://imagemagick.org/script/download.php

GhostScript
https://www.ghostscript.com/doc/9.21/Install.htm

Poppler
https://blog.alivate.com.au/poppler-windows/

XAMPP
https://www.apachefriends.org/download.html

Create a virtual environment :
$conda create -n virtualenvironmentname

Other installments:
Rest of the installments are done by writing the following in Anaconda prompt--

$ pip install tesseract flask flask-restplus schedule flask_sqlalchemy PyPDF2 Wand

$pip install https://github.com/pdftables/python-pdftables-api/archive/master.tar.gz

pdftables_api provides with a free key for short duration and for that you need to generate the key from the provided link, further usage requires you to buy it. https://pdftables.com/pdf-to-excel-api









