from flask import Flask
from scraper.routes import routes
from scraper.actions import action
import threading
import time
import os
import asyncio


app = Flask(__name__)

def periodic_check():
    while True:
        print("Periodic check")
        asyncio.run(action())
        time.sleep(10)  # Aguardar 5 minutos (300 segundos)

app.register_blueprint(routes, url_prefix="/api/v1")

if __name__ == "__main__":

    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        # Inicia a thread para a verificação periódica apenas no processo principal
        check_thread = threading.Thread(target=periodic_check)
        check_thread.daemon = True  # Permite que a thread termine quando o programa principal termina
        check_thread.start()

    app.run(debug=True, host="0.0.0.0", port=2500)
