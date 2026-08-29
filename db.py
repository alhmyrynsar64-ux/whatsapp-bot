import os,sqlite3
from dotenv import load_dotenv
load_dotenv(); DB=os.getenv('DB_PATH','database/bot.db')
os.makedirs(os.path.dirname(DB) or '.',exist_ok=True)
def get():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
 c.executescript(open('database/schema.sql',encoding='utf-8').read()); return c
def init():
 c=get()
 for k,v in [('welcome','مرحباً بك في بوت الأرقام الافتراضية 📱'),('support','للدعم تواصل مع الإدارة.')]:
  c.execute('INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)',(k,v))
 if c.execute('SELECT COUNT(*) FROM buttons').fetchone()[0]==0:
  for x in [('📱 شراء رقم','numbers',0),('💰 رصيدي','balance',0),('📦 طلباتي','orders',1),('➕ إيداع','deposit',1),('📜 السجل','history',2),('🆘 الدعم','support',2)]:
   c.execute('INSERT INTO buttons(title,callback,row_no) VALUES(?,?,?)',x)
 c.commit(); c.close()
