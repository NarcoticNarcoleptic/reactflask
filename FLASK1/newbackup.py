import os
import tempfile
from flask import Flask, render_template, request,jsonify,make_response
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
#from sentence_transformers import SentenceTransformer
import time
from qdrant_client.http import models

app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "http://localhost:3000"}})
qdrant_url = os.getenv('QDRANT_URL', default='localhost')
qdrant_port = os.getenv('QDRANT_PORT', default=6333)
COLLECTION_NAME = os.getenv('COLLECTION_NAME')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
cohere_api_key = os.environ.get('cohere_api_key')

client = QdrantClient(host=qdrant_url, port=qdrant_port)
qdrant = None  # Initialize qdrant as a global variable


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





# Global variables for rate limiting
rate_limit_interval = 10  # 30 seconds
last_request_time = 0
rate_limit_reached = False

@app.route('/upload', methods=['POST'])
def upload_pdf():
    global qdrant  # Access the global qdrant variable
    global rate_limit_reached  # Access the rate_limit_reached flag
    global last_request_time  # Access the last request time
   
    # Check if enough time has passed since the last request
    current_time = time.time()
    if current_time - last_request_time < rate_limit_interval:
        return "Rate limit reached. Please try again later."

    pdf = request.files['pdf']
    
    if pdf:
        if not rate_limit_reached:
            
            with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(pdf.read())
            
            loader = PyPDFLoader(tmp_file.name)
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
            pages = loader.load_and_split(text_splitter)

            # Create embeddings
            embeddings = OpenAIEmbeddings()
            qdrant = Qdrant.from_documents(pages, embeddings, url=qdrant_url, collection_name=COLLECTION_NAME)

            # Update the last request time after a successful request
            last_request_time = current_time

            return "PDF uploaded successfully!"
        else:
            return "Rate limit reached. Please try again later."

    else:
        return "File upload failed."







@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    return response


QDRANT_HOST = "localhost"
QDRANT_PORT = 6333

@app.route('/create_collection', methods=['POST', 'OPTIONS'])
def create_qdrant_collection():
    if request.method == 'OPTIONS':
        # Set the CORS headers to allow the origin
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response
    try:
        data = request.get_json()
        if 'collection_name' in data:
            collection_name = data['collection_name']
        else:
            return jsonify({'error': 'Collection name is missing in the request data.'}, 400)

        # Initialize QdrantClient
        qdrant_client = QdrantClient(QDRANT_HOST, port=QDRANT_PORT)

        # Create the collection with the specified parameters
        vectors_config = models.VectorParams(size=100, distance=models.Distance.COSINE)
        qdrant_client.create_collection(collection_name=collection_name, vectors_config=vectors_config)

        return jsonify({'message': f'Qdrant collection "{collection_name}" created successfully.'})
    except Exception as e:
        return jsonify({'error': f'Failed to create Qdrant collection: {str(e)}'}, 500)













@app.route('/ask', methods=['GET', 'POST'])

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
