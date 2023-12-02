from flask import Flask, request, session, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES

from src.server import DataCollector, face_matching_probability
from src.server.common import url_to_img


app = Flask(__name__)

# Configure the upload settings
photos = UploadSet("photos", IMAGES)
app.config["UPLOADED_PHOTOS_DEST"] = "uploads"
configure_uploads(app, photos)


@app.route('/api/v1/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    try:
        session['data_collector'] = DataCollector(username, password)
        return jsonify({'message': 'Login successful'}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to login', 'error': e}), 401


@app.route('api/v1/search_people', methods=['POST'])
def search_people():
    # Check if the POST request has the file part
    if "photo" not in request.files:
        return jsonify({"error": "No file part"}), 400

    photo = request.files["photo"]

    # If the user does not select a file, the browser submits an empty file without a filename
    if photo.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # Save the uploaded file
    filename = photos.save(photo)
    file_url = photos.url(filename)

    refresh_offset = True
    if 'refresh_offset' in request.form.keys():
        refresh_offset = request.form.get('refresh_offset')

    keywords = None
    if 'keywords' in request.form.keys():
        keywords = request.form.get('keywords')

    chunk_size = 100
    if 'chunk_size' in request.form.keys():
        chunk_size = request.form.get('chunk_size')

    if refresh_offset:
        session['data_collector'].refresh_offset()

    for profile in session['data_collector'].search(keywords, chunk_size):
        input_photo = url_to_img(file_url)
        profile_photo = url_to_img(profile['photo'])

        if face_matching_probability(profile_photo, input_photo) > 0.4:
            yield jsonify(profile)
