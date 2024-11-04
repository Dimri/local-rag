import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# from utils.embeddings import create_embeddings
# from utils.chat import ask

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

UPLOAD_DIR = "./data/uploads"
current_file_path = ""

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "hello world"}


@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global current_file_path
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    current_file_path = file_location
    # save the file
    try:
        with open(file_location, "wb") as f:
            f.write(await file.read())
        return {"info": f"file '{file.filename}' saved at '{file_location}'"}
    except Exception as e:
        print("error occured: ", e)
        raise HTTPException(status_code=500, detail="File upload fail")


# @app.post("/query")
# def answer_query(query: str):
#     embeddings = create_embeddings(current_file_path)
#     llm_response = ask(query=query, embeddings=embeddings)
#     return {"response": llm_response}
