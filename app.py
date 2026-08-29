import os,sys
from flask import Flask,request,redirect,session
sys.path.insert(0,os.path.dirname(os.path.dirname(__file__)))
from database.db import get,init
from dotenv import load_dotenv
load_dotenv();init();app=Flask(__name__);app.secret_key=os.getenv('ADMIN_PASSWORD','change')
CSS='<style>body{font-family:Arial;background:#f3f5f9;margin:0;color:#172033}.nav{background:#111827;color:white;padding:18px}.w{max-width:1100px;margin:20px auto;padding:12px}.c{background:white;padding:18px;border-radius:15px;margin:12px 0;box-shadow:0 2px 12px #0001}.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}a,button{background:#2563eb;color:white;padding:10px;border:0;border-radius:8px;text-decoration:none}input{padding:9px;margin:5px;width:90%}table{width:100%;background:white;border-collapse:collapse}td,th{padding:9px;border-bottom:1px solid #eee}</style>'
def page(x):return '<html lang=ar dir=rtl><meta charset=utf-8>'+CSS+'<div class=nav>نصار الحميري — لوحة تحكم الأرقام</div><div class=w>'+x+'</div></html>'
@app.before_request
def guard():
 if request.endpoint not in ('login','static') and not session.get('a'):return redirect('/')
@app.route('/',methods=['GET','POST'])
def login():
 if request.method=='POST' and request.form.get('p')==os.getenv('ADMIN_PASSWORD'):session['a']=1;return redirect('/dashboard')
 return page('<div class=c><h2>🔐 دخول الإدارة</h2><form method=post><input type=password name=p placeholder=كلمة_المرور><button>دخول</button></form></div>')
@app.route('/dashboard')
def dashboard():
 c=get();u=c.execute('select count(*) n from users').fetchone()['n'];b=c.execute('select coalesce(sum(balance),0)n from users').fetchone()['n'];s=c.execute('select count(*) n from suppliers').fetchone()['n'];o=c.execute("select count(*) n from orders where status='pending'").fetchone()['n'];c.close()
 return page(f'<div class=g><div class=c>👥 المستخدمون<h2>{u}</h2></div><div class=c>💰 الأرصدة<h2>{b:.2f}</h2></div><div class=c>🌐 الموردون<h2>{s}</h2></div><div class=c>📦 طلبات معلقة<h2>{o}</h2></div></div><div class=g><a href=/suppliers>🌐 الموردون</a><a href=/products>📱 المنتجات</a><a href=/orders>📦 الطلبات</a><a href=/transactions>💳 الإيداعات</a><a href=/users>👥 المستخدمون</a><a href=/buttons>🔘 الأزرار</a><a href=/logout>خروج</a></div>')
@app.route('/suppliers',methods=['GET','POST'])
def suppliers():
 c=get()
 if request.method=='POST':c.execute('insert into suppliers(name,base_url,api_key) values(?,?,?)',(request.form['name'],request.form['url'],request.form.get('key','')));c.commit()
 rs=c.execute('select * from suppliers').fetchall();c.close()
 body='<div class=c><h2>🌐 إضافة مورد</h2><p>يجب أن يدعم المورد API رسميًا. إدخال رابط موقع وحده لا يضمن التكامل.</p><form method=post><input name=name placeholder=اسم_المورد><input name=url placeholder=رابط_API><input name=key placeholder=API_Key type=password><button>إضافة</button></form></div><div class=c><table><tr><th>الاسم</th><th>API</th></tr>'+''.join(f"<tr><td>{r['name']}</td><td>{r['base_url']}</td></tr>" for r in rs)+'</table></div><a href=/dashboard>عودة</a>';return page(body)
@app.route('/products',methods=['GET','POST'])
def products():
 c=get();ss=c.execute('select * from suppliers where enabled=1').fetchall()
 if request.method=='POST':c.execute('insert into products(supplier_id,country,service,price) values(?,?,?,?)',(request.form['sid'],request.form['country'],request.form['service'],float(request.form['price'])));c.commit()
 rs=c.execute('select p.*,s.name sn from products p join suppliers s on s.id=p.supplier_id').fetchall();c.close()
 opts=''.join(f"<option value={s['id']}>{s['name']}</option>" for s in ss)
 return page(f'<div class=c><h2>📱 إضافة منتج</h2><form method=post><select name=sid>{opts}</select><input name=country placeholder=الدولة><input name=service placeholder=الخدمة><input name=price type=number step=.01 placeholder=السعر><button>إضافة</button></form></div><div class=c><table><tr><th>ID</th><th>المورد</th><th>الدولة</th><th>الخدمة</th><th>السعر</th></tr>'+''.join(f"<tr><td>{r['id']}</td><td>{r['sn']}</td><td>{r['country']}</td><td>{r['service']}</td><td>{r['price']}</td></tr>" for r in rs)+'</table></div><a href=/dashboard>عودة</a>')
@app.route('/orders')
def orders():
 c=get();rs=c.execute('select * from orders order by id desc limit 200').fetchall();c.close();return page('<div class=c><h2>📦 الطلبات</h2><table><tr><th>ID</th><th>المستخدم</th><th>الدولة</th><th>الخدمة</th><th>السعر</th><th>الحالة</th></tr>'+''.join(f"<tr><td>{r['id']}</td><td>{r['user_id']}</td><td>{r['country']}</td><td>{r['service']}</td><td>{r['price']}</td><td>{r['status']}</td></tr>" for r in rs)+'</table></div><a href=/dashboard>عودة</a>')
@app.route('/transactions')
def transactions():
 c=get();rs=c.execute('select * from transactions order by id desc limit 200').fetchall();c.close();return page('<div class=c><h2>💳 الإيداعات</h2><table><tr><th>ID</th><th>المستخدم</th><th>المبلغ</th><th>الحالة</th><th>إجراء</th></tr>'+''.join(f"<tr><td>{r['id']}</td><td>{r['user_id']}</td><td>{r['amount']}</td><td>{r['status']}</td><td><a href='/tx/{r['id']}/ok'>قبول</a> <a href='/tx/{r['id']}/no'>رفض</a></td></tr>" for r in rs)+'</table></div><a href=/dashboard>عودة</a>')
@app.route('/tx/<int:i>/<a>')
def tx(i,a):
 c=get();r=c.execute('select * from transactions where id=?',(i,)).fetchone()
 if r and r['status']=='pending':
  if a=='ok':c.execute('update users set balance=balance+? where id=?',(r['amount'],r['user_id']));c.execute("update transactions set status='approved' where id=?",(i,))
  else:c.execute("update transactions set status='rejected' where id=?",(i,))
  c.commit()
 c.close();return redirect('/transactions')
@app.route('/users')
def users():
 c=get();rs=c.execute('select * from users order by id desc limit 300').fetchall();c.close();return page('<div class=c><h2>👥 المستخدمون</h2><table><tr><th>ID</th><th>Username</th><th>الرصيد</th><th>الحالة</th><th></th></tr>'+''.join(f"<tr><td>{r['id']}</td><td>{r['username'] or '-'}</td><td>{r['balance']:.2f}</td><td>{'موقوف' if r['blocked'] else 'نشط'}</td><td><a href='/u/{r['id']}'>تبديل</a></td></tr>" for r in rs)+'</table></div><a href=/dashboard>عودة</a>')
@app.route('/u/<int:i>')
def toggle(i):
 c=get();c.execute('update users set blocked=1-blocked where id=?',(i,));c.commit();c.close();return redirect('/users')
@app.route('/buttons',methods=['GET','POST'])
def buttons():
 c=get()
 if request.method=='POST':c.execute('insert into buttons(title,callback,row_no) values(?,?,?)',(request.form['title'],request.form['callback'],int(request.form.get('row',0))));c.commit()
 rs=c.execute('select * from buttons order by row_no,id').fetchall();c.close()
 return page('<div class=c><h2>🔘 الأزرار</h2><form method=post><input name=title placeholder=نص_الزر><input name=callback placeholder=callback><input name=row type=number value=0><button>إضافة</button></form></div><div class=c><table><tr><th>الزر</th><th>الوظيفة</th></tr>'+''.join(f"<tr><td>{r['title']}</td><td>{r['callback']}</td></tr>" for r in rs)+'</table></div><a href=/dashboard>عودة</a>')
@app.route('/logout')
def logout():session.clear();return redirect('/')
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.getenv('PORT','8000')))
