import os
import re
import time
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.embeddings import add_embeddings, load_embedding_model

from utils.chat import ask
from utils.vectordb import vectordb_client, upload_documents
from concurrent.futures import ThreadPoolExecutor

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# global variablesk
UPLOAD_DIR = "./data/uploads"
current_file_path = ""
device = "cuda"
client = None
collection = None
collection_ready = False
embedding_model = load_embedding_model()
executor = ThreadPoolExecutor(max_workers=2)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class ChatMessage(BaseModel):
    message: str


def create_collection(file_path: str):
    global collection, collection_ready, client
    # remove any non-digit and non-alpha characters from the file_path
    # collection name should start with an alphabet
    collection_name = "A" + re.sub(
        r"[^A-Za-z0-9]", repl="", string=file_path.split("/")[-1]
    )
    client = vectordb_client()
    try:
        collection_names = list(client.collections.list_all(simple=True).keys())
        print(f"{collection_names = }")
    except Exception as e:
        print(e)

    if collection_name not in collection_names:
        # create collection
        try:
            print(f"Creating a new collection: {collection_name}")
            collection = client.collections.create(name=collection_name)
            chunks = add_embeddings(file_path, embedding_model=embedding_model)
            upload_documents(chunks, collection)
            print(f"Created collection: '{collection_name}'")
        except Exception as e:
            print(e)
            client.close()
    else:
        # get collection
        try:
            print("collection already present")
            collection = client.collections.get(collection_name)
        except Exception as e:
            print(e)
            client.close()

    collection_ready = True


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "hello world"}


@app.post("/upload/")
async def upload_file(file: UploadFile, background_tasks: BackgroundTasks):
    global current_file_path
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    current_file_path = file_path
    # save the file
    try:
        with open(file_path, "wb") as f:
            f.write(await file.read())
    except Exception as e:
        print("error occured: ", e)
        raise HTTPException(status_code=500, detail="File upload fail")

    # create embeddings in the background
    background_tasks.add_task(executor.submit, create_collection, file_path)

    return {"info": f"file '{file.filename}' saved at '{file_path}'"}


@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    # wait for embeddings to get ready
    waited_time = 0
    max_wait_time = 20
    while not collection_ready and waited_time < max_wait_time:
        print(f"Time elapsed: {waited_time:2}. Collection is getting ready. Waiting...")
        time.sleep(1)
        waited_time += 1

    if not collection_ready:
        return HTTPException(status_code=500, detail="emebddings not created")

    user_message = chat_message.message
    print(f"{current_file_path = }")
    if not client.is_ready():
        client.connect()
    try:
        llm_response, context_items = ask(query=user_message, collection=collection)
    except Exception as e:
        print(e)
        return HTTPException(status_code=500, detail="emebddings not created")
    finally:
        client.close()

    return {"reply": llm_response, "context": context_items}
