from flask import Blueprint, jsonify
#import check_profiles
from bot import check_profiles, update_profile_infos, get_payments_profiles
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

@routes.route('/profieinfos/<string:profileid>/<string:atualiza>', methods=['GET'])
async def profileinfos(profileid, atualiza):

    result = await asyncio.gather(update_profile_infos(profileid, atualiza))

    return jsonify({'result': 'success'})

@routes.route('/createpayments/<string:profileid>/<string:fechamento>', methods=['GET'])
async def createpayments(profileid, fechamento):
    # Define a função que será executada em segundo plano
    result = await asyncio.gather(get_payments_profiles(profileid, fechamento))

    return jsonify({'message': 'Iniciando rota assíncrona'})
 