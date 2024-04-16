from flask import Blueprint, jsonify

routes = Blueprint('routes', __name__)

@routes.route('/hello', methods=['GET'])
def hello():
    return jsonify({'hello': 'I can'})


