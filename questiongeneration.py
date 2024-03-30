
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
# from chromadb.utils import embedding_functions
# from chromadb import Chroma

load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_pdf_text(file_path):
    extracted_text = ""
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        for page in pdf_reader.pages:
            extracted_text += page.extract_text()
    return extracted_text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    # new_db = FAISS.load_local("faiss_index", embeddings,allow_dangerous_deserialization=True)
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    
    vector_store.save_local("faiss_index")

def get_conversational_chain_mcq():

    prompt_template = """
    Given the provided {context}, your task is to generate multiple-choice questions (MCQs) based on Bloom's Taxonomy. For each identified topic in the document, create MCQs for each level of Bloom's Taxonomy as follows:

        1) Remembering (Knowledge-based questions):
        - Ask factual questions that require recalling information from the context.
        - Sample question stems: Who, What, When, Where, Define, Identify, List, etc.
        
        2) Understanding (Comprehension-based questions):
        - Ask questions that require understanding the meaning, interpreting, exemplifying, summarizing, or inferring information from the context.
        - Sample question stems: Explain, Describe, Summarize, Illustrate, Interpret, etc.
        
        3) Applying (Application-based questions):
        - Ask questions that require applying information from the context to new situations or solving problems.
        - Sample question stems: How would you use/apply...? What would happen if...? Solve/Calculate, etc.
        
        4) Analyzing (Analysis-based questions):
        - Ask questions that require breaking down information into parts, finding patterns, identifying causes/reasons, and making inferences.
        - Sample question stems: Analyze, Differentiate, Categorize, Compare/Contrast, etc.
        
        5) Evaluating (Evaluation-based questions):
        - Ask questions that require making judgments, evaluating ideas or solutions, and justifying decisions based on the context.
        - Sample question stems: Evaluate, Justify, Critique, Argue for/against, etc.
        
        6) Creating (Synthesis-based questions):
        - Ask questions that require generating new ideas, products, or ways of viewing things based on the context.
        - Sample question stems: Design, Construct, Develop, Formulate, Propose, etc.

       
        **Important note:- for each level create maximum of 2 questions only (strictly)
        
        output format :- 
        an array of 
            -bloom taxonomy tag
            -question
            -option 1
            -option 2
            -option 3
            -option 4 
            -answer(option name like option1, option2, option3, option4)
            -explanation
            give in list of objects format and give the closing tag for the list (mandatory) 
            

        
    Question:{question}
        
    Answer:""
        """
    model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def get_conversational_chain():

    prompt_template = """
    if they asked to create the question based on bloom taxonomy then 
    first in the context identify the topics in document. 
    for each identified topic in the document , generate questions for each level of Bloom's Taxonomy from the given context  as follows:

    1) Remembering (Knowledge-based questions):
            Ask factual questions that require recalling information from the context.
            Sample question stems: Who, What, When, Where, Define, Identify, List, etc.
    2) Understanding (Comprehension-based questions):
            Ask questions that require understanding the meaning, interpreting, exemplifying, summarizing, or inferring information from the context.
            Sample question stems: Explain, Describe, Summarize, Illustrate, Interpret, etc.
    3) Applying (Application-based questions):
            Ask questions that require applying information from the context to new situations or solving problems.
            Sample question stems: How would you use/apply...? What would happen if...? Solve/Calculate, etc.
    4) Analyzing (Analysis-based questions):
            Ask questions that require breaking down information into parts, finding patterns, identifying causes/reasons, and making inferences.
            Sample question stems: Analyze, Differentiate, Categorize, Compare/Contrast, etc.
    5) Evaluating (Evaluation-based questions):
            Ask questions that require making judgments, evaluating ideas or solutions, and justifying decisions based on the context.
            Sample question stems: Evaluate, Justify, Critique, Argue for/against, etc.
    6) Creating (Synthesis-based questions):
            Ask questions that require generating new ideas, products, or ways of viewing things based on the context.
            Sample question stems: Design, Construct, Develop, Formulate, Propose, etc.
    and return it in the format of dictionary with value as the list of question
    
    

    Context:\n {context}?\n
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                             temperature=0.3)

    prompt = PromptTemplate(template = prompt_template, input_variables = ["context", "question"])
    chain = load_qa_chain(model, chain_type="stuff", prompt=prompt)

    return chain

def user_input(option):
    user_question = "generate questions based on bloom taxonomy in the mcq type"
    embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")
    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    docs = new_db.similarity_search(user_question)
    # subjective questions
    if option ==1:
        chain = get_conversational_chain()
    else:
        chain = get_conversational_chain_mcq()
    # print(docs, user_question)
    response = chain({'question': user_question,'input_documents':docs})
    # print(response)
    return response




    
    
