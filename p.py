from flask import Flask, jsonify, request
import uuid
import asyncio

app = Flask(__name__)

# Dicionário para mapear IDs de tarefa para status
task_status = {}

async def get_payments_profiles(profileid, fechamento, task_id):
    # Simulando uma tarefa assíncrona
    await asyncio.sleep(5)
    task_status[task_id] = "Concluída"

@app.route('/createpayments/<string:profileid>/<string:fechamento>', methods=['GET'])
def createpayments(profileid, fechamento):
    # Gerar um ID de tarefa único
    task_id = str(uuid.uuid4())

    # Iniciar a tarefa assíncrona
    asyncio.create_task(get_payments_profiles(profileid, fechamento, task_id))

    # Retornar o ID da tarefa ao cliente
    return jsonify({'task_id': task_id})

@app.route('/task_status/<string:task_id>', methods=['GET'])
def check_task_status(task_id):
    # Verificar o status da tarefa com base no ID da tarefa
    status = task_status.get(task_id, "Tarefa não encontrada")
    return jsonify({'status': status})

if __name__ == '__main__':
    app.run(debug=True)

