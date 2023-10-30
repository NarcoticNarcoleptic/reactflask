import os
import tempfile
from flask import Flask, render_template, request,jsonify
from langchain.embeddings import CohereEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from qdrant_client import QdrantClient
from langchain.callbacks import get_openai_callback
import qdrant_client
from langchain.chains import RetrievalQA
from flask_cors import CORS 
from sentence_transformers import SentenceTransformer

app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "http://localhost:3000"}})
qdrant_url = os.getenv('QDRANT_URL', default='localhost')
qdrant_port = os.getenv('QDRANT_PORT', default=6333)
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
cohere_api_key = os.environ.get('cohere_api_key')

client = QdrantClient(host=qdrant_url, port=qdrant_port)
qdrant = None  # Initialize qdrant as a global variable
model = SentenceTransformer('all-MiniLM-L6-v2')

# Function to create the vector store
def get_vector_store():
    client = qdrant_client.QdrantClient(
        os.getenv("QDRANT_HOST"),
        api_key=os.getenv("QDRANT_API_KEY")
    )
    
    embeddings = OpenAIEmbeddings()

    vector_store = Qdrant(
        client=client, 
        collection_name=os.getenv("COLLECTION_NAME"), 
        embeddings=embeddings,
    )
    
    return vector_store


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/upload', methods=['POST'])
def upload_pdf():
    global qdrant  # Access the global qdrant variable
    pdf = request.files['pdf']
    if pdf:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(pdf.read())
        
        loader = PyPDFLoader(tmp_file.name)
        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
        pages = loader.load_and_split(text_splitter)

        # Create embeddings
        embeddings = OpenAIEmbeddings()
        qdrant = Qdrant.from_documents(pages, embeddings, url=qdrant_url, collection_name=COLLECTION_NAME)
        
        return "PDF uploaded successfully!"
    else:
        return "File upload failed."

@app.route('/answer', methods=['GET', 'POST'])

def ask_question():
    try:
        user_question = request.json.get('question')
        print(user_question)
        if user_question:
            vector_store = get_vector_store()
            qa = RetrievalQA.from_chain_type(
                llm=OpenAI(model_name="gpt-3.5-turbo-16k"),
                chain_type="stuff",
                retriever=vector_store.as_retriever()
            )

            # Process the user's question
            answer = qa.run(user_question)
            print("Answer:", answer) 
            # Return the answer as JSON
            return jsonify({"answer": answer})
            
        else:
            return jsonify({"error": "Invalid question provided."})
    
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run()
