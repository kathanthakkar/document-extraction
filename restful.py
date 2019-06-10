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
from pdf2image import convert_from_path
import io
from PIL import Image
from wand.image import Image as wi
from PyPDF2 import PdfFileMerger
from pytesseract import pytesseract
import pandas as pd
import pdftables_api
c = pdftables_api.Client('3sz7npouifhm')

app = Flask(__name__)
api = Api(app)
UPLOAD_FOLDER = r'G:\Internship\Main\Flask App\document-extraction\uploadedpdfs'
file_upload = reqparse.RequestParser()
file_upload.add_argument('pdf_file',  
                         type=werkzeug.datastructures.FileStorage, 
                         location='files', 
                         required=True, 
                         help='Upload a pdf file')

a_keyword = api.model('Keyword',{'keyword' : fields.String('The Keyword ?')})
keyword_list = []
filename = ''

@api.route('/upload/')
class my_file_upload(Resource):
    @api.expect(file_upload)
    def post(self):
        global filename
        args = file_upload.parse_args()
        if args['pdf_file'].mimetype == 'application/pdf':
            destination = UPLOAD_FOLDER
            if not os.path.exists(destination):
                os.makedirs(destination)
            fileextract = str(args['pdf_file'])
            filename = fileextract[fileextract.find('\'') + 1: fileextract.find('.pdf')]
            filename = filename + '.pdf'
            xls_file = os.path.join(destination, filename)
            args['pdf_file'].save(xls_file)
        else:
            abort(404)
        return {'status': 'Done'}
    
    def get(self):
        # Enter the name of the pdf to be processed in filename
        global filename
        filepath  = 'uploadedpdfs/' + filename
        pdf = wi(filename = filepath, resolution = 300)
        pdfImage = pdf.convert('jpeg')
        
        imageBlobs = []
        i = 0
        for img in pdfImage.sequence:
            imgPage = wi(image = img)
            imageBlobs.append(imgPage.make_blob('jpeg'))
            print(i)
            i = i+1
        	
        page = []
        recognized_text = []
        j = 0
        for imgBlob in imageBlobs:
            im = Image.open(io.BytesIO(imgBlob))
            text = pytesseract.image_to_string(im, lang = 'eng')
            recognized_text.append(text)
            print(j)
            j = j+1
            
        # Enter the keyword you want to search for 
        keyword = keyword_list[-1].get('keyword')
        key =  keyword.split(' ', 1)[0]
        result = [k for k in recognized_text if k.startswith(keyword)]
        for l in result:
            str1 = ''.join(l)
            page = recognized_text.index(str1)
            print("page is:", page + 1)
            pagefound = page + 1
            break
        
        #Page Number loop for keyword
        res = "".join(recognized_text)
        ls = []
        for x in range(1,len(recognized_text) + 1):
            mat = "Page "+str(x)+" of "+key
            if res.find(mat) != -1:
                ls.append(x)
            else:
                if ls == []:
                    #print("page of "+keyword+" is: "+str(pagefound))
                    ls.append(pagefound)
                    break
                else:
                    for i in range(0, len(ls)): 
                        ls[i] = int(ls[i]) 
                    print("Number of pages for "+keyword+" is "+str(max(ls)))
                    break
        ls2=[]
        if len(ls) > 1: 
            for z in range(max(ls)):
                fin = z + pagefound
                z1 = str(fin)
                ls2.append(z1)
            for p1 in ls2:
                print("page of "+keyword+" is: "+p1)
        else:
            ls2 = ls
            for p1 in ls2:
                print("page of "+keyword+" is: "+str(p1)) 
        # Save pdf to jpg page-wise
        fname = os.path.splitext(os.path.basename(filepath))[0]
        pages = convert_from_path(filepath, 843)
        i=1
        for page in pages:
            savepath = 'Images/'+fname+'_'+str(i)+'.jpeg'
            page.save(savepath, 'JPEG')
            i = i + 1
            
        #Convert selected page from jpg to hOCR pdf
        for i in ls2:    
            currentpagepath = 'Images/'+fname+'_'+str(i)+'.jpeg'
            pdf_name = 'PDFs/'+fname+'_'+str(i)
            pytesseract.run_tesseract(currentpagepath, pdf_name, lang=None, config="hocr", extension='pdf')
            
        # Merge all pdfs into one
        pdf_list=[]
        for i in ls2:
            pdf_name = 'PDFs/'+fname+'_'+str(i)+'.pdf'
            pdf_list.append(pdf_name)
            
        pdf_output_name = key + '.pdf'
        merger = PdfFileMerger()
        for pdf in pdf_list:
            merger.append(open(pdf, 'rb'))
        with open(pdf_output_name, 'wb') as fout:
            merger.write(fout)
            
            
        #Parse the hOCR for Tables and save it to xlsx
        excel_output_name = key + '.xlsx'
        c.xlsx(pdf_output_name,excel_output_name)
        #xls_file = pd.ExcelFile(excel_output_name)
        #xls_file.sheet_names
        #df = xls_file.parse('Sheet1')
        #return df
        return {'status': 'Done'}

@api.route('/keywordpage/')
class keyword_input(Resource):
    @api.marshal_with(a_keyword, envelope='Keyword Searched for:')
    def get(self):
        print (keyword_list[-1])
        return keyword_list[-1]
    
    @api.expect(a_keyword)
    def post(self):
        keyword_list.append(api.payload)
        return {'result' : 'Your Keyword is being searched!'},201
    
    
if __name__ == "__main__":
    app.run()