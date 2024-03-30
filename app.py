from flask import Flask, render_template, request, redirect, url_for, session
import csv
import pyrebase
import firebase
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import storage
import os
from questiongeneration import get_pdf_text, get_text_chunks, get_vector_store, get_conversational_chain, user_input
import json
from supabase import create_client, Client
from dotenv import load_dotenv
from studenttest import retrivequestions
from flask import jsonify
from datetime import datetime
# from studenttest import getmytests
import re
remembering = {
    'elie': 1,
    'medium':2,
    'low':3
}
understanding = {
    'elie': 1,
    'medium':2,
    'low':2
}
applying = {
    'elie': 1,
    'medium':2,
    'low':1
}
analyzing = {
    'elie': 2,
    'medium':1,
    'low':3
}
evaluating = {
    'elie': 2,
    'medium':1,
    'low':0
}
creating = {
    'elie': 3,
    'medium':1,
    'low':0
}


load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

app = Flask(__name__)
app.secret_key = "your_secret_key"  

#authentication 

firebaseConfig = {
    'apiKey': "AIzaSyC5IgBXaslXo7Y_wl2LZVDyPY9_1muA8V0",
    'authDomain': "edutransform-33efe.firebaseapp.com",
    'projectId': "edutransform-33efe",
    'storageBucket': "edutransform-33efe.appspot.com",
    'messagingSenderId': "714003630570",
    'appId': "1:714003630570:web:0239ee658c18e9f6224a93",
    'measurementId': "G-93VTMCF22Q",
    'databaseURL': ''
  };

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# Firestore database 
cred = credentials.Certificate('credentials.json')
application = firebase_admin.initialize_app(cred)
db = firestore.client()
docs = db.collections()

# creating an empty session
session = []
user = {
    'collection': '',
    'docid': '',
    
}
truetestkeys = []
userdetails = {}

# path for saving the files 
current_dir = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(current_dir, 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Funtions 
def getdata():
    org = db.collection(user['collection'])
    students = org.where('role', '==', 'student').stream()
    teachers = org.where('role', '==', 'teacher').stream()
    teachers_list, students_list = [], []
    for doc in students:
            students_list.append(doc.to_dict())
    for doc in teachers:
            teachers_list.append(doc.to_dict())
    print(students_list, teachers_list)
    
def getmytests():
    print(f"get my  tests {userdetails}")

    user_class = userdetails['class']
    user_section = userdetails['section']
    # Regular expression to extract class, section, subject, and lesson from true_keys
    key_regex = r'(\d+)-(\w+)-(\w+)-(\d+)'
    
    tests = []
    
    for key in truetestkeys:
        match = re.match(key_regex, key)
        print(f" in getmytests function {key_regex}, {key}, {match}")
        if match:
            matched_class = match.group(1)
            matched_section = match.group(2)
            matched_subject = match.group(3)
            matched_lesson = match.group(4)
            print(matched_class, matched_section)
            if matched_class == user_class and matched_section == user_section:
                tests.append((matched_subject, matched_lesson))
    
    print(f"in the get my tests {tests}")
    return tests
    
def getquestions():
    data = supabase.table("questions").select("question, class").eq("subject", userdetails['subject']).execute()
def reset():
    global userdetails, user
    userdetails= {}
    user = {
    'collection': '',
    'docid': '',
    
}
def gettestdetails():
    global truetestkeys
    doc_ref = db.collection(user['collection']).document("test")
    doc = doc_ref.get().to_dict()
    if doc:
        for key, value in doc.items():
            if value is True:
                truetestkeys.append(key)
    print(f"getting test in fucntion {truetestkeys}")
    return truetestkeys

    

def createaccount(name, email, password, organization):
    data = {
        'name': name,
        'email': email,
        'password': password,
        'role':'admin'
        
    }
    
    try: 
        auth.create_user_with_email_and_password(email, password)
        db.collection(organization).document('admin1').set(data)
        return "created"
    except Exception as e:
        print(f" create account error {e}")
        return "error"
    
    
def createquestions(path,classname, subject, lesson_number):
    raw_text = get_pdf_text(path)
    text_chunks = get_text_chunks(raw_text)
    get_vector_store(text_chunks)
    #subjective questions-1 
    # mcqs - 0
    response_mcq = user_input(0)
    print(response_mcq)
    response_mcq = eval(str(response_mcq['output_text']+' "}] '))
    print(response_mcq)

    
    for dictionary in response_mcq:
        for key, value in dictionary.items():
            if value == "null":
                dictionary[key] = None
    
    # print(response_mcq[2])
    for question in response_mcq:
        print(question)
        data = []
        
        data.append({
                'class': classname,
                'subject': subject,
                'lesson': lesson_number,
                'bloom_taxonomy_tag': question['bloom_taxonomy_tag'] if 'bloom_taxonomy_tag' in question else None,
                'question': question['question'] if 'question' in question else None,
                'option 1': question['option1'] if 'option1' in question else None,
                'option 2': question['option2'] if 'option2' in question else None,
                'option 3': question['option3'] if 'option3' in question else None,
                'option 4': question['option4'] if 'option4' in question else None,
                'answer': question['answer'] if 'answer' in question else None,
                'explanation': question['explanation'] if 'explanation' in question else None
            })
        res = supabase.table('mcq_questions').insert(data).execute()
        print("insertion done")

        
    
    return response_mcq
    
def createstudentaccount(file_path):
    print("entered createstudentaccount function")
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            print(row)
            name = row['name']
            email = row['email']
            class_name = row['class']
            section = row['section']
            parentmail = row['parentmail']
            
            data = {
                'name': name,
                'email': email,
                'class': class_name,
                'section': section,
                'parentmail': parentmail,
                'role': 'student'
            }
            studentpassword=123456
            auth.create_user_with_email_and_password(email,studentpassword)
            db.collection(user['collection']).add(data)
            print(f"added student {name}")
            
    print("added all students succesfully")
    

def createteacheraccount(file_path):    
    print("entered createteacheraccount function")
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            name = row['Name']
            email = row['Email']
            subject_name = row['subject_name']
            data = {
                'name': name,
                'email': email,
                'subject_name': subject_name,
                'role': 'teacher'
            }
            teacherpassword=123456
            auth.create_user_with_email_and_password(email,teacherpassword)
            db.collection(user['collection']).add(data)
            print(f"added teacher {name}")
            
    print("added teacher succesfully")
    
    
def createadminaccount(file_path):    
    print("entered createadminaccount function ")
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        print("started")
        for row in csv_reader:
            name = row['Name']
            email = row['Email']
            data = {
                'name': name,
                'email': email,
                
                'role': 'admin'
            }
            adminpassword=123456
            auth.create_user_with_email_and_password(email,adminpassword)
            db.collection(user['collection']).add(data)
            print(f"added admin {name}")
            
    print("added admin succesfully")
    

# def adddetails(file_path):    
#     print("entered")
#         # Open the CSV file for reading
#     with open(file_path, 'r') as csvfile:
#         # Create a CSV reader object
#         csv_reader = csv.DictReader(csvfile)
        
#         # Loop over each row in the CSV file
#         print("started")
#         for row in csv_reader:
#             # Extract details from the row
#             name = row['Name']
#             email = row['Email']
            

            
#             # Create a dictionary to store the details
#             data = {
#                 'name': name,
#                 'email': email,
#                 'role': 'admin'
#             }
            
#             # Add the details to the Firestore database
#             # Replace 'students' with the name of your Firestore collection
#             adminpassword=123456
#             auth.create_user_with_email_and_password(email,adminpassword)
#             db.collection(user['collection']).add(data)
#             print(f"added {name}")
            
#     print("added succesfully")
  
def createtest(collection, classname, section, subject, lesson):
    print(collection)
    
    collection_ref = db.collection(collection).document("test")
    testid = f"{classname}-{section}-{subject}-{lesson}"
    collection_ref.update({testid: True})
    

    
def get_profile(collection,docid):
    global userdetails
    userdetails = {}
    print(f"get profile function {collection},{docid}")
    doc_ref = db.collection(collection).document(docid)
    doc = doc_ref.get()
    if doc.exists:
        userdetails = doc.to_dict()
    print(f"get profile function {userdetails}")

        
    
def get_docid(email):
    global user
    user['docid']=''
    user['collection']=''
    print(f"geting docid of {email}")
    doc_found = False
    docs = db.collections()
    for collection in docs:
        print("entered1")
        query = collection.where('email', '==', email).limit(1).stream()
        print("entered2")
        for doc in query:
            print("entered 3")
            print(doc.id)
            
            dummy_id = doc.id
            print("checking in get_docid")
            user['docid']=doc.id
            user['collection']=collection.id
            print(f" got docid {user}")
            break
        
    print(f" got docid {user}")
  
    return dummy_id
        
            
            



@app.route('/', methods=['GET', 'POST'])
def home():
    # if user in session:
    #     return render_template('home/logged.html')
    # else:
    #     return render_template('home/notlogged.html')
    return render_template('home/notlogged.html')

@app.route('/notlogged', methods=['GET', 'POST'])
def notlogged():
    return render_template('home/notlogged.html')

@app.route('/signin', methods = ['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # print(request.form)
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        organization = request.form['Organization']
        
        if createaccount(name, email, password, organization)== 'created':
            get_docid(email)
            get_profile(user['collection'],user['docid'])
            session.append(email)
            return render_template('home/logged.html')
    return render_template('auth/signin.html')

@app.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        # print(request.form)
        email = request.form['email']
        password = request.form['password']
        try:
            userw = auth.sign_in_with_email_and_password(email, password)
            print("authentication done")
            session.append(email)
            dummyvariable = get_docid( email)
            print("entering in login")
            print(user)
            if user['docid']:
                get_profile(user['collection'],user['docid'])
                print(userdetails)
                if userdetails:
                    if userdetails['role'] == 'teacher':
                        return redirect(url_for('teacher', docid=user['docid']))
                    elif userdetails['role'] == 'student':
                        gettestdetails()
                        return redirect(url_for('student', docid = user['docid']))
                    elif userdetails['role'] == 'admin':
                        return redirect(url_for('admin', docid = user['docid']))
        except Exception as e:
            print(f"error:- {e}")
            pass
    return render_template('auth/login.html')
@app.route('/stduent/<docid>', methods=['GET', 'POST'])
def student(docid):
    return render_template('home/student.html')

@app.route('/teacher/<docid>', methods=['GET', 'POST'])
def teacher(docid):
    return render_template('home/teacher.html')

@app.route('/admin/<docid>',methods=['GET', 'POST'])
def admin(docid):
    return render_template('home/logged.html')

@app.route('/logout', methods=['GET','POST'])
def logout():
    reset()
    if session:
        session.pop()
    return redirect(url_for('notlogged'))

@app.route('/profile', methods=['GET','POST'])
def profile():
    user_details = userdetails
    # getdata()
    print(user_details)
    return render_template('components/profile.html',user_details=user_details)

@app.route('/workflow', methods=['GET','POST'])
def workflow():
    if request.method == 'POST':
        if 'student_csv' in request.files and 'teacher_csv' in request.files and 'admin_csv' in request.files :

            print(request.files)
            student_csv = request.files['student_csv']
            teacher_csv = request.files['teacher_csv']
            admin_csv = request.files['admin_csv']
            if student_csv.filename != '' and teacher_csv.filename != '' and admin_csv.filename != '':
                # student data 
                file_path_student = os.path.join(app.config['UPLOAD_FOLDER'], 'student.csv')
                student_csv.save(file_path_student)
                createstudentaccount(file_path_student)

                # teacher data 
                file_path_teacher = os.path.join(app.config['UPLOAD_FOLDER'], 'teacher.csv')
                teacher_csv.save(file_path_teacher)
                print(file_path_teacher)
                createteacheraccount(file_path_teacher)
                
                # admin data
                file_path_admin = os.path.join(app.config['UPLOAD_FOLDER'], 'admin.csv')
                admin_csv.save(file_path_admin)
                createadminaccount(file_path_admin)
                
               # details of the organization 
                # file_path_details = os.path.join(app.config['UPLOAD_FOLDER'], 'details.csv')
                # student_csv.save(file_path_details)
                # adddetails(file_path_details)

                
                
            else:
                print("No file selected!")
                return 'No file selected!'
            
    return render_template('components/workflow.html')


@app.route('/update_lesson', methods=['POST', 'GET'])
def update_lesson():
    
    if request.method == 'POST':
        
        # print(request.form)
        classname = request.form['class']
        # section = request.form['section']
        subject = request.form['subject']
        lesson_number = request.form['lesson_number']
        
        if 'lesson_pdf' in request.files:
            lesson = request.files['lesson_pdf']
        
            file_path_lesson = os.path.join(app.config['UPLOAD_FOLDER'], 'lesson.pdf')
            lesson.save(file_path_lesson)
            response = createquestions(file_path_lesson, classname, subject, lesson_number)
            print(f"updated mcq type questions are:- {response['output_text']}")
            # response_text=json.loads(response['output_text'])
            # print(response_text['Remembering'])
            # for topic in response_text:
            #     for question in response_text[topic]:
            #         pass
                    # data = supabase.table("descriptive").insert({'class':classname, 'subject': subject, 'lesson': lesson_number, 'bloom_taxonomy_tag': topic, 'question': question}).execute()

                
            # response_text = json.loads(response_text)
    return render_template('components/update_lesson.html')

@app.route('/taketest', methods=['POST', 'GET'])
def taketest():
    subject = request.args.get('subject')
    lesson = request.args.get('lesson')
    classname = request.args.get('classname')
    print(f" take test printing {subject}, {classname}, {lesson}")

    if request.method == 'POST':
        print("entered request of score ")
        score_data = request.get_json()
        score = score_data.get('score')
        if score_data and score:
            print(f'Received score: {score} for subject: {subject} in lesson: {lesson}')
            print(user)
            # Here, you can save the score to the database or perform any other necessary actions
            test_id = f"{userdetails['class']}-{subject}-{lesson}"
            test_id_score = f"{userdetails['class']}-{subject}-{lesson}-{score}"

# Combine both updates into a single call
            org = db.collection(user['collection']).document(user['docid'])
            org.update({test_id: True,test_id_score: score})

            return jsonify({'message': 'Score received successfully'})

    response = retrivequestions(subject, classname, lesson)
    if response:
        return render_template('components/taketest.html', response=response[1])

    return render_template('components/taketest.html')

@app.route('/maketest', methods=['POST', 'GET'])
def maketest():
    if request.method == 'POST':
        class_value = request.form['class']
        section_value = request.form['section']
        subject_value = request.form['subject']
        lesson_value = request.form['lesson']
        print(user['collection'])
        createtest(user['collection'],class_value, section_value, subject_value, lesson_value)
    return render_template('components/maketest.html')


@app.route('/tests',methods=['POST', 'GET'])
def testpage():
    # print(userdetails)
    test = getmytests()
    # print(test)
    classname = userdetails['class']
    return render_template('components/testpage.html', tests=test, classname=classname)



if __name__ == '__main__':
    app.run(debug=True)
