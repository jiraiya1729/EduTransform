import os 
from supabase import create_client, Client

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

def retrivequestions(subject, classname, lessonname):
    conditions = {
        'subject': subject.lower(),
        'class': classname,
        'lesson': lessonname
    }
    columns = ['question', 'option1', 'option2', 'option3', 'option4', 'answer']
    data, count = supabase.table('mcq_questions').select('*').match(conditions).execute()
    
    print(data)


retrivequestions("science", 1, 1)