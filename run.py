from threading import Thread
from admin.app import app
from bot.main import run
if __name__=='__main__':
 Thread(target=lambda:app.run(host='0.0.0.0',port=8000),daemon=True).start()
 run()
