import json
from bot import check_profiles, update_profile_infos, get_payments_profiles, create_data_bubble, get_user_profiles

BASE_URL = 'https://consium.com.br/api/1.1/obj/esoteric-actions'

async def update_action(action_id, status):
    url = f'{BASE_URL}/{action_id[0]}'
    json_update = json.dumps({"Status": status})
    response = await create_data_bubble(json_update, url, 'update')
    print(response.status_code)

async def atualia_converter(update):
    if update == 'Sim':
        return 'True'
    else:
        return 'False'

async def process_action(item):
    status = item['Status']
    act = item['Action']
    site = item['SiteId']
    id = item['_id'],
    update = await atualia_converter(item['Update']),
    fechamento = item['Fechamento'] 
    if status in ['Aguardando Servidor', 'Erro!!!', 'Em Andamento']:
        if act == 'Get Profiles':
            print('Buscando por novos usuários')
            try:
                await update_action(id, 'Em Andamento')
                await check_profiles(site, id)
                await update_action(id, 'Concluido')
            except:
                await update_action(id, 'Erro!!!')
        if act == 'Get Profiles Infos':
            print('Atualizando dados dos perfis')
            try:
                await update_action(id, 'Em Andamento')
                await update_profile_infos(site, update, id)
                await update_action(id, 'Concluido')
            except:
                await update_action(id, 'Erro!!!')
            print('Get Profiles Infos')
        print(act)
        if act == 'Payments':
            print('Criando pagamentos')
            try:
                await update_action(id, 'Em Andamento')
                await get_payments_profiles(site, fechamento)
                await update_action(id, 'Concluido')
            except:
                await update_action(id, 'Erro!!!')

async def action():
    try:
        response = await get_user_profiles(site_id=None, url_input=BASE_URL)
        for item in response:
            await process_action(item)
    except Exception as e:
        print(f"Error fetching user profiles: {e}")

