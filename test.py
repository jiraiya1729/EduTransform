import firebase 
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials

user = {
    'collection': '',
    'docid': '',
    
}
cred = credentials.Certificate('credentials.json')
application = firebase_admin.initialize_app(cred)
db = firestore.client()
docs = db.collections()

email = "varunchowdary172969@gmail.com"
for collection in docs:
        query = collection.where('email', '==', email).limit(1).stream()
        for doc in query:
            print(doc.id)
            user['docid']=doc.id
            user['collection']=collection.id
            
        print(user)
        
        
#  sample format of output 
    
#         **Output:**
#         [
#             {
#                 'question': 'Your question here',
#                 'options': ['A. Option A', 'B. Option B', 'C. Option C', 'D. Option D'],
#                 'answer': 'A',
#                 'level': 'Remembering'
#             },
#             {
#                 'question': 'Your question here',
#                 'options': ['A. Option A', 'B. Option B', 'C. Option C', 'D. Option D'],
#                 'answer': 'B',
#                 'level': 'Understanding'
#             },
#             ... (more MCQs for other levels)
#         ]