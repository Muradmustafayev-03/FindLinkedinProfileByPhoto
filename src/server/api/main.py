from flask import Flask

from src.server import DataCollector, face_matching_probability


app = Flask(__name__)


@app.route('/api/v1/find_person', methods=['POST'])
def find_person():
    pass
