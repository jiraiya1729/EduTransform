from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

supabase = create_client(url, key)

# data = supabase.table("questions").select("*").execute()
data = supabase.table("questions").insert({'class':8, 'section': 'A', 'subject': 'Science', 'lesson': 2, 'bloom_taxonomy_tag': 'create', 'question': 'Create an experiment?'}).execute()
print(data)
