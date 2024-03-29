from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# data = supabase.table("questions").select("*").execute()

data = supabase.table("mcq_questions").insert({
    'class':8,

    'subject': 'English',
    'lesson': 4,
    'bloom_taxonomy_tag': 'understanding ',
    'question': 'understanding checking 1',
    'option 1':'incorrect1',
    'option 2': 'incorrect2',
    'option 3': 'correct3',
    'option 4': 'incorrect4',
    'answer':'option3'
    }).execute()
data = supabase.table("mcq_questions").insert({
    'class':8,

    'subject': 'English',
    'lesson': 4,
    'bloom_taxonomy_tag': 'understanding ',
    'question': 'understanding checking 2',
    'option 1':'correct1',
    'option 2': 'incorrect2',
    'option 3': 'incorrect3',
    'option 4': 'incorrect4',
    'answer':'option1'
    }).execute()
data = supabase.table("mcq_questions").insert({
    'class':8,

    'subject': 'English',
    'lesson': 4,
    'bloom_taxonomy_tag': 'understanding ',
    'question': 'understanding checking 3',
    'option 1':'incorrect1',
    'option 2': 'incorrect2',
    'option 3': 'incorrect3',
    'option 4': 'correct4',
    'answer':'option 4'
    }).execute()

print(data)
