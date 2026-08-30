import os,logging
from dotenv import load_dotenv
from telegram import Update,InlineKeyboardButton,InlineKeyboardMarkup
from telegram.ext import Application,CommandHandler,CallbackQueryHandler,MessageHandler,ContextTypes,filters
from db import get,init
load_dotenv(); TOKEN=os.getenv('BOT_TOKEN'); ADMIN_ID=int(os.getenv('ADMIN_ID','0')); logging.basicConfig(level=logging.INFO)
def kb():
 c=get(); rows={}
 for r in c.execute('SELECT title,callback,row_no FROM buttons WHERE enabled=1 ORDER BY row_no,id'): rows.setdefault(r['row_no'],[]).append(InlineKeyboardButton(r['title'],callback_data=r['callback']))
 c.close(); return InlineKeyboardMarkup([v for _,v in sorted(rows.items())])
async def start(u,ctx):
 x=u.effective_user;c=get();c.execute('INSERT OR IGNORE INTO users(id,username,first_name) VALUES(?,?,?)',(x.id,x.username,x.first_name));c.commit()
 msg=c.execute("SELECT value FROM settings WHERE key='welcome'").fetchone()['value']; blocked=c.execute('SELECT blocked FROM users WHERE id=?',(x.id,)).fetchone()['blocked'];c.close()
 if blocked:return await u.message.reply_text('🚫 حسابك موقوف.')
 await u.message.reply_text(msg,reply_markup=kb())
async def cb(u,ctx):
 q=u.callback_query;await q.answer();uid=q.from_user.id;c=get();r=c.execute('SELECT * FROM users WHERE id=?',(uid,)).fetchone()
 if r['blocked']:c.close();return await q.edit_message_text('🚫 حسابك موقوف.')
 if q.data=='balance': t=f"💰 رصيدك: {r['balance']:,.2f}"
 elif q.data=='numbers':
  rs=c.execute('SELECT p.id,p.country,p.service,p.price,s.name FROM products p JOIN suppliers s ON s.id=p.supplier_id WHERE p.enabled=1 AND s.enabled=1').fetchall();t='📱 الأرقام المتاحة:\n\n'+('\n'.join(f"#{x['id']} | {x['country']} | {x['service']} | {x['price']}" for x in rs) if rs else 'لا توجد أرقام متاحة.');ctx.user_data['action']='buy'
 elif q.data=='orders':
  rs=c.execute('SELECT id,country,service,status FROM orders WHERE user_id=? ORDER BY id DESC LIMIT 10',(uid,)).fetchall();t='📦 طلباتك:\n'+('\n'.join(f"#{x['id']} {x['country']} {x['service']} — {x['status']}" for x in rs) if rs else 'لا توجد طلبات.')
 elif q.data=='deposit':ctx.user_data['action']='deposit';t='➕ أرسل مبلغ الإيداع.'
 elif q.data=='history':
  rs=c.execute('SELECT kind,amount,status FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10',(uid,));t='📜 السجل:\n'+('\n'.join(f"{x['kind']} {x['amount']} — {x['status']}" for x in rs) if rs else 'لا توجد عمليات.')
 else:t=c.execute("SELECT value FROM settings WHERE key='support'").fetchone()['value']
 c.close();await q.edit_message_text(t,reply_markup=kb())
async def msg(u,ctx):
 a=ctx.user_data.get('action')
 if not a:return
 uid=u.effective_user.id
 try:n=float(u.message.text.replace(',','').strip())
 except:
  if a=='buy':
   try:pid=int(u.message.text.strip())
   except:return await u.message.reply_text('❌ أرسل رقم المنتج.')
   c=get();p=c.execute('SELECT * FROM products WHERE id=? AND enabled=1',(pid,)).fetchone()
   if not p:c.close();return await u.message.reply_text('❌ المنتج غير موجود.')
   bal=c.execute('SELECT balance FROM users WHERE id=?',(uid,)).fetchone()['balance']
   if bal<p['price']:c.close();return await u.message.reply_text('❌ الرصيد غير كافٍ.')
   c.execute('INSERT INTO orders(user_id,supplier_id,product_id,country,service,price) VALUES(?,?,?,?,?,?)',(uid,p['supplier_id'],pid,p['country'],p['service'],p['price']));c.commit();c.close();ctx.user_data.clear();return await u.message.reply_text('⏳ تم إنشاء الطلب للمورد.')
  return await u.message.reply_text('❌ أرسل مبلغاً صحيحاً.')
 if n<=0:return await u.message.reply_text('❌ المبلغ غير صحيح.')
 c=get();c.execute('INSERT INTO transactions(user_id,kind,amount,note) VALUES(?,?,?,?)',(uid,'إيداع',n,'مراجعة المشرف'));c.commit();c.close();ctx.user_data.clear();await u.message.reply_text('✅ تم تسجيل الإيداع للمراجعة.')
 if ADMIN_ID:await ctx.bot.send_message(ADMIN_ID,f'🔔 إيداع جديد: {uid} — {n}')
def run():
 init();app=Application.builder().token(TOKEN).build();app.add_handler(CommandHandler('start',start));app.add_handler(CallbackQueryHandler(cb));app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,msg));app.run_polling()
if __name__=='__main__':run()
