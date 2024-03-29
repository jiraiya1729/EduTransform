from supabase import create_client, Client
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
from firebase_admin import storage
from datetime import datetime
timestamp = datetime.now()
import re

    # Format the timestamp as a string
time_string = timestamp.strftime('%Y%m%d%H%M%S')

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# cred = credentials.Certificate('credentials.json')
# application = firebase_admin.initialize_app(cred)
# db = firestore.client()
# docs = db.collections()


def retrivequestions(subject, classname, lessonname):
    conditions = {
        'subject': subject,
        'class': classname,
        'lesson': lessonname
    }
    columns = ['question', 'option1', 'option2', 'option3', 'option4', 'answer']
    data, count = supabase.table('mcq_questions').select('*').match(conditions).execute()
    print(data)
    return data
    # print(data[1][9]['question'])
    
retrivequestions("science", 8, 2)
# from datetime import datetime
# city_ref = db.collection("vnr vignana jyothi test").document("data")
# data = {
#     "maths8": 0,
#     "science8": 0,
#     "social8": 0
# }

# city_ref.set(data)

    
    
def getmytests(alltests, userdetails):
    print(userdetails)
    # user_class = userdetails['class']
    user_section = userdetails['section']
    # Regular expression to extract class, section, subject, and lesson from true_keys
    key_regex = r'class(\d+)-section(\w+)-(\w+)-lesson(\d+)'
    
    tests = []
    
    for key in alltests:
        match = re.match(key_regex, key)
        
        if match:
            matched_class = match.group(1)
            matched_section = match.group(2)
            matched_subject = match.group(3)
            matched_lesson = match.group(4)
            
            if matched_class == user_class and matched_section == user_section:
                tests.append((matched_subject, f"Lesson {matched_lesson}"))
    
    print(tests)
    
    

    
