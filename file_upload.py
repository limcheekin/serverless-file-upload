from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tempfile
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/upload")
async def create_upload_file(file: UploadFile = File(...)):
    chunk_size = 1024 * 1024  # 1 MB

    with tempfile.NamedTemporaryFile(
            mode='wb',
            buffering=chunk_size,
            delete=os.getenv("DELETE", True)) as temp:
        while True:
            chunk = await file.read(chunk_size)
            if not chunk:
                break
            temp.write(chunk)
        temp.flush()
    response = {"filename": file.filename, "tempfilename": temp.name}
    print(response)
    return response


def test_upload_file():
    from fastapi.testclient import TestClient
    client = TestClient(app)
    with open("text.json", "rb") as file:
        response = client.post("/upload", files={"file": file})
    assert response.status_code == 200
    print(response.json())


if os.getenv("RUNTIME") == "aws-lambda":
    from mangum import Mangum
    handler = Mangum(app)

if __name__ == "__main__":
    # test_upload_file()
    import uvicorn
    uvicorn.run(
        app, host=os.getenv("HOST", "localhost"), port=int(os.getenv("PORT", 8000))
    )
