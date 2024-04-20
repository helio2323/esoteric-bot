from flask import Blueprint, jsonify
#import check_profiles
from bot import check_profiles
import asyncio

routes = Blueprint('routes', __name__)

@routes.route('/hello', methods=['GET'])
def hello():
    return jsonify({'hello': 'I can'})

@routes.route('/profile/<string:profileid>', methods=['GET'])
async def profile(profileid):

    result = await asyncio.gather(check_profiles(profileid))

    return jsonify({'result': 'success'})
    #chama a funcao check_prfiles

