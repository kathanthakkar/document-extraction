# -*- coding: utf-8 -*-
"""
Created on Tue Jun 18 13:18:04 2019

@author: Anshul
"""

################################ IMPORT LIBRARIES #############################
import os
from flask import Flask, abort
import werkzeug
import pickle
from pdf2image import convert_from_path
import io
from PIL import Image
from wand.image import Image as wi
from PyPDF2 import PdfFileMerger
from pytesseract import pytesseract
from flask_sqlalchemy import SQLAlchemy
import pdftables_api
from flask_restplus import Api, Resource, fields, reqparse
import logging
import queue as Queue
import threading
import time
import schedule

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
c = pdftables_api.Client('dxpdtg8uyuer', timeout = (60,3600)) # Get your API key from https://pdftables.com/

############################## INITIALIZATION #################################
app = Flask(__name__)
api = Api(app)
app.config['SWAGGER_UI_JSONEDITOR'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/doc_extraction_db'   #Enter your database name instead of doc_extraction_db
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
UPLOAD_FOLDER = os.path.dirname(os.path.abspath("__file__"))
if not os.path.isdir(os.path.join(UPLOAD_FOLDER,"remaining")):
    os.mkdir('remaining')
if not os.path.isdir(os.path.join(UPLOAD_FOLDER,"Images")):
    os.mkdir('Images')
file_upload = reqparse.RequestParser()
file_upload.add_argument('pdf_file',  
                         type=werkzeug.datastructures.FileStorage, 
                         location='files', 
                         required=True, 
                         help='Upload a pdf file')

def job():
    sql = db.session.query(info_table).filter(info_table.status == 'Pending').first()
    sql.status = 'Working'
    fileid = sql.id
    savename = sql.savenamedb
    keyworddb = sql.keyworddb
    outfilename = sql.outputfiledb
    db.session.commit()
    with open(outfilename + '.txt','rb') as fp:
        recognized_text = pickle.load(fp)
    filepath  = 'remaining/' + savename
    content_text = ''
    # Enter the keyword you want to search for 
    keyword = keyworddb
    key =  keyword.split(' ', 1)[0]
    result = [k for k in recognized_text if k.startswith(keyword)]
    for l in result:
        str1 = ''.join(l)
        page = recognized_text.index(str1)
        print("page is:", page + 1)
        pagefound = page + 1
        break
    
    #Page Number loop for keyword
    print('Page Number loop for keyword')
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
    print('Save pdf to jpg page-wise')
    fname = os.path.splitext(os.path.basename(filepath))[0]
    pages = convert_from_path(filepath, 843) # Resolution can be changed according to your use
    i=1
    for page in pages:
        savepath = 'Images/'+fname+'_'+str(i)+'.jpeg'
        page.save(savepath, 'JPEG')
        i = i + 1
    
    #Save in contentdb 
    print('Save in contentdb')
    for i in ls2:
        content_text = content_text + "|||" + recognized_text[int(i)-1]
    sql = info_table.query.filter_by(id = fileid).first()
    sql.contentdb = content_text
        
    
    #Convert selected page from jpg to hOCR pdf
    print('Convert selected page from jpg to hOCR pdf')
    for i in ls2:    
        currentpagepath = 'Images/'+fname+'_'+str(i)+'.jpeg'
        pdf_name = 'PDFs/'+fname+'_'+str(i)
        pytesseract.run_tesseract(currentpagepath, pdf_name, lang=None, config="hocr", extension='pdf')
        
    # Merge all pdfs into one
    print('Merge all pdfs into one')
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
    print('Parse the hOCR for Tables and save it to xlsx')
    excel_output_name = key + '.xlsx'
    c.xlsx(pdf_output_name,excel_output_name)
    
    sql.status = 'Completed'
    print('Status : completed And updating Jsondb')
    json_string = {}
    json_string['json_data'] = []
    json_string['json_data'].append({  
        'taskid': sql.id,
        'filename': sql.filenamedb,
        'doctypeid': sql.doctype,
        'accuracy': sql.accuracy,
        'keywordsearched': sql.keyworddb,
        'content': sql.contentdb
    })
    sql.jsondb = json_string
    db.session.commit()
        


def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        jobqueue.task_done()

jobqueue = Queue.Queue()
############################### DECLARATION ###################################
file_upload.add_argument('docid', type=int, help='you want to find')
a_keyword = api.model('Keyword',{'keyword' : fields.String('The Keyword ?')})
a_status = api.model('Status',{'status' : fields.Integer('The ID number ?')})
a_keywordadd = api.model('keywordadd',{'id' : fields.Integer('The ID number ?'), 'keyword' : fields.String('The Keyword ?')})
a_doctypeid = api.model('doctypeid',{'refid' : fields.Integer('The ID number ?'), 'docid' : fields.Integer('The docid ?')})
keyword_list = []
status_list = []
filename = ''
itemdb = ''
page = []
res = ''
valkey = []
valid = []
newsearch = []
content_text = ''
accuracy = 0
keywordadd_list = []
idadd_list = []
savename = ''
search_list = []
json_string = {}
savelist = []

############################### DATABASE ######################################
class info_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filenamedb = db.Column(db.String(120), unique=False, nullable=True)
    savenamedb = db.Column(db.String(120), unique=False, nullable=True)    
    status = db.Column(db.String(120), unique=False, nullable=True)
    keyworddb = db.Column(db.String(120), unique=False, nullable=True)
    foundKeywords = db.Column(db.String(999), unique=False, nullable=True)
    accuracy = db.Column(db.Float, unique=False, nullable=True)
    doctype = db.Column(db.Integer, unique=False, nullable=True)
    outputfiledb = db.Column(db.String(120), unique=False, nullable=True)
    contentdb = db.Column(db.String(100000), unique=False, nullable=True)
    jsondb = db.Column(db.String(100000), unique=False, nullable=True)
    
    def __repr__(self):
        return '<%r %r %r %r %r %r %r %r %r %r>' % (self.savenamedb,self.filenamedb,self.status,self.keyworddb,self.foundKeywords,self.accuracy,self.doctype,self.outputfiledb,self.contentdb,self.jsondb)

class key_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    keywords = db.Column(db.String(999), unique=False, nullable=True)
    
    def __repr__(self):
        return '<%r>' % (self.keyword)

db.create_all()

############################## RESTPLUS FUNCTIONS #############################

# UPLOAD A FILE AND SELECT DOCTYPE
@api.route('/upload/')
class upload_file(Resource):
    
    @api.expect(file_upload)
    def post(self):
        args = file_upload.parse_args()
        docid  = args['docid'] 
        if args['pdf_file'].mimetype == 'application/pdf':
            destination = UPLOAD_FOLDER
            if not os.path.exists(destination):
                os.makedirs(destination)
            fileextract = str(args['pdf_file'])
            filename = fileextract[fileextract.find('\'') + 1: fileextract.find('.pdf')]
            filename = filename + '.pdf' 
            user_1 = info_table(filenamedb = filename, status='Uploading', doctype = docid)
            db.session.add(user_1)
            db.session.commit()
            item = db.session.query(info_table).filter(info_table.filenamedb == filename).all()
            print(item[-1].id)
            itemdb = item[-1].id
            savename = 'file' + str(itemdb) + '.pdf' 
            xls_file = os.path.join(destination, savename)
            args['pdf_file'].save(xls_file)
            item2 = db.session.query(info_table).filter(info_table.id == itemdb).first()
            item2.savenamedb = savename
            db.session.commit()
            searchquery = key_table.query.filter_by(id = docid).first()
            search_list = (searchquery.keywords).split(',')
            print(search_list)
            
            filepath  = 'remaining/' + savename
            pdf = wi(filename = filepath, resolution = 300) #Resolution can be changed according to your use
            pdfImage = pdf.convert('jpeg')
            recognized_text = []
            imageBlobs = []
            i = 0
            for img in pdfImage.sequence:
                
                imgPage = wi(image = img)
                imageBlobs.append(imgPage.make_blob('jpeg'))
                print(i)
                i = i+1
            j = 0
            for imgBlob in imageBlobs:
                im = Image.open(io.BytesIO(imgBlob))
                text = pytesseract.image_to_string(im, lang = 'eng')
                recognized_text.append(text)
                print(j)
                j = j+1
            newsearch = []    
            res = "".join(recognized_text)
            for k in search_list:
                if res.find(k) != -1:
                    newsearch.append(k)
            myList = []
            accuracy = ((len(newsearch)) / (len(search_list))) * 100
            myList = ','.join(map(str, newsearch))
            
            item = db.session.query(info_table).filter(info_table.savenamedb == savename).all()
            print(item[-1].id)
            itemdb = item[-1].id
            with open(f'outfile{itemdb}.txt', 'wb') as fp:
                pickle.dump(recognized_text, fp)
            item2 = db.session.query(info_table).filter(info_table.id == itemdb).first()
            item2.accuracy = accuracy
            item2.foundKeywords = myList
            item2.outputfiledb = f'outfile{itemdb}'
            db.session.commit()
            item3 = db.session.query(info_table).filter(info_table.id == itemdb).first()
            newsearch = item3.foundKeywords
            accuracy = item3.accuracy
            
            
            return {'result' : f' Accuracy for found keywords={newsearch} is {accuracy} and Your id for further reference: {itemdb}'},201

        else:
            abort(404)
        
        return {'status': 'Done'}


# KEYWORD SEARCH WITHIN THE DOCUMENT
@api.route('/keyword/search/')
class keyword_input(Resource):
    @api.expect(a_keywordadd)
    def post(self):
        keywordadd_list.append(api.payload)
        ref_id = keywordadd_list[-1].get('id')
        keyword_searched = keywordadd_list[-1].get('keyword')
        item = db.session.query(info_table).filter(info_table.id == ref_id).first()
        item.keyworddb =  keyword_searched
        item.status = 'Pending'
        db.session.commit()
        schedule.every(120).seconds.do(jobqueue.put, job)
        
        return {'result' : f'Your id for further reference: {ref_id}'},201
    

# PROCESS
@api.route('/Process/')
class process(Resource):
    def get(self):
        worker_thread = threading.Thread(target=worker_main)
        worker_thread.start()
        while 1:
            schedule.run_pending()
            time.sleep(180)






#   EXTRA FUNCTIONS

# DISPLAY AVAILABLE DOCTYPE's
@api.route('/Doctype/Available/')
class display_doctype(Resource):
    def get(self):
        vals = key_table.query.all()
        for vali in vals:
            valid.append(vali.id)
            valkey.append(vali.keywords)
       
        s = ''
        for i in range(0, len(valid)):
            s = s + f'({valid[i]} = {valkey[i]})'
            
        return {'result' : s},201

# ADD MORE KEYWORDS TO A DOCTYPE
@api.route('/Doctype/Keywordadd/')
class key_add(Resource):
    @api.expect(a_keywordadd)
    def post(self):
        vals = key_table.query.all()
        for vali in vals:
            valid.append(vali.id)
            valkey.append(vali.keywords)
        keywordadd_list.append(api.payload)
        doc_id = keywordadd_list[-1].get('id')
        keywords = keywordadd_list[-1].get('keyword')
        if doc_id in valid:
            qu = key_table.query.filter_by(id = doc_id).first()
            qu.keywords = qu.keywords + ',' + keywords
            db.session.commit()
            return {'result' : f'{keywords} added in docid: {doc_id}'},201

        else:
            user_3 = key_table(id = doc_id, keywords = keywords)
            db.session.add(user_3)
            db.session.commit()
            valid.append(doc_id)
            return {'result' : f'New docid: {doc_id} and keyword: {keywords} added'},201

# CHECK STATUS OF A DOCUMENT
@api.route('/status/')
class status_update(Resource):        
    @api.expect(a_status)
    def post(self):
        status_list.append(api.payload)
        statusid = status_list[-1].get('status')
        statusreturn = db.session.query(info_table).filter(info_table.id == statusid).first()
        print(statusreturn.status)
        statusdb = statusreturn.status

        return {'result' : f'{statusdb}'},201


################################## RUN THE APP ################################
if __name__ == "__main__":
    app.run()
