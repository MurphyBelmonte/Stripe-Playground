import json
from flask import jsonify

def jsonify_model(model):
    return jsonify(json.loads(model))
