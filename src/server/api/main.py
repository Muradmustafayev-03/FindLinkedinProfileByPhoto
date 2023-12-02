from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import cv2
import numpy as np

from src.server import DataCollector, face_matching_probability, url_to_img

app = FastAPI()


@app.post("api/v1/find_profiles")
async def find_profiles(
        username: str = Form(...),
        password: str = Form(...),
        photo: UploadFile = File(...),
        keywords: str = Form(None),
        chunk_size: int = Form(100),
):
    """
    Finds LinkedIn profiles of people found on the photo
    """
    try:
        data_collector = DataCollector(username, password)

        content = await photo.read()
        arr = np.frombuffer(content, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        matches = []
        for profile in data_collector.search(keywords, chunk_size):
            photo = url_to_img(profile['photo'])
            if face_matching_probability(img, photo):
                matches.append(profile)
        return JSONResponse(content=matches, status_code=200)

    except Exception as e:
        return JSONResponse(content={"message": f"Error processing photo: {str(e)}", "status": "error"},
                            status_code=500)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
