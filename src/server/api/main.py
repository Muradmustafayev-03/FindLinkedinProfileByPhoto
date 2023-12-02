from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from starlette.requests import Request

from src.server import DataCollector, face_matching_probability
from src.server.common import url_to_img

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency to get the current data collector session
def get_data_collector(request: Request = Depends()):
    return request.session.get("data_collector")


@app.post('/api/v1/login')
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        request.session["data_collector"] = DataCollector(username, password)
        return JSONResponse(content={'message': 'Login successful'}, status_code=200)
    except Exception as e:
        return JSONResponse(content={'message': 'Failed to login', 'error': str(e)}, status_code=401)


@app.post('/api/v1/search_people')
async def search_people(
        photo: UploadFile = File(...),
        refresh_offset: bool = Form(True),
        keywords: str = Form(None),
        chunk_size: int = Form(100)
):
    data_collector: DataCollector = get_data_collector()

    if not photo:
        raise HTTPException(status_code=400, detail={"error": "No file part"})

    if photo.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(status_code=415, detail={"error": "Unsupported Media Type"})

    # Limit the file size
    max_file_size = 2 * 1024 * 1024  # 2 MB
    contents = await photo.read()
    if len(contents) > max_file_size:
        raise HTTPException(status_code=413, detail={"error": "Payload Too Large"})

    file_url = photo.url

    if not file_url:
        raise HTTPException(status_code=400, detail={"error": "No selected file"})

    if refresh_offset:
        data_collector.refresh_offset()

    results = []

    for profile in data_collector.search(keywords, chunk_size):
        input_photo = url_to_img(file_url)
        profile_photo = url_to_img(profile['photo'])

        if face_matching_probability(profile_photo, input_photo) > 0.4:
            results.append(profile)

    return results

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app=app, host="127.0.0.1", port=8000)
