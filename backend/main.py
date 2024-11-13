import os
import time
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from utils.embeddings import create_embeddings
from utils.chat import ask
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
embeddings = None
embeddings_ready = False  # initially embeddings for the file are not ready
executor = ThreadPoolExecutor(max_workers=2)

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


class ChatMessage(BaseModel):
    message: str


def generate_embeddings(file_path: str):
    global embeddings, embeddings_ready
    print(f"creating embeddings for file: '{file_path}'")
    embeddings = create_embeddings(pdf_path=file_path).to(device)
    embeddings_ready = True
    print(f"created.")


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
    background_tasks.add_task(executor.submit, generate_embeddings, file_path)

    return {"info": f"file '{file.filename}' saved at '{file_path}'"}


@app.post("/chat")
async def chat_endpoint(chat_message: ChatMessage):
    # wait for embeddings to get ready
    waited_time = 0
    max_wait_time = 10
    while not embeddings_ready and waited_time < max_wait_time:
        print(f"Time elapsed: {waited_time:2}. Embeddings are not ready. Waiting...")
        time.sleep(1)
        waited_time += 1

    if not embeddings_ready:
        return HTTPException(status_code=500, detail="emebddings not created")

    user_message = chat_message.message
    print(f"{current_file_path = }")
    llm_response = ask(query=user_message, embeddings=embeddings)
    return {"reply": llm_response}
