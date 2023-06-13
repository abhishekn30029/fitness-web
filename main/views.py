from django.shortcuts import render,redirect
from django.db import connection
from django.contrib import messages
login=int(0)
dt={'name':'','id':0,'cstatus':False,'tstatus':False}
# Create your views here.
def index(request):
    print(dt['name'])
    return render(request,"index.html",dt)
def trainers(request):
    message=''
    cursor=connection.cursor()
    if request.method=='POST':
        tid=int(request.POST.get('tid',0))
        cursor.execute("select cid from subscription")
        cid=cursor.fetchall()
        ls=[element for innerlist in cid for element in innerlist]
        if dt['id']==0:
            message='please login to subscribe'
            
        elif dt['id'] not in ls: 
            cursor.execute("insert into subscription(tid,cid,sdate,ldate) values({},{},curdate(),date_add(curdate(),interval 30 day))".format(tid,dt['id']))
            message='successfully subscribed please check in your trainer'
        else:
            message='your already subscribed for training please continue that training'
    cursor=connection.cursor()
    cursor.execute("select t.fullname,t.price,r.rev_stars,t.id,r.count from trainer t,avg_rating r where t.id=r.id")
    trainer=cursor.fetchall()
    trainer_list=[]
    for i in trainer:
        trainer_list.append({'tname':i[0],'price':i[1],'rating':i[2],'id':i[3],'count':i[4] if i[4]!=None else 0})
    return render(request,"trainers.html",{'dest':trainer_list,'dt':dt,'msg':message})
def clientlogin(request):
    message=''
    if request.method=='POST':
        
        cursor=connection.cursor()
        d=request.POST
        if(len(d)>3):
            cursor.execute("select email from client")
            email=cursor.fetchall()
            ls=[element for innerlist in email for element in innerlist]
            mail=d.get('email')
            if mail in ls:
                message='user already exists please login'
                return render(request,'clientlogin.html',{'msg':message})
            else:
                cursor.execute("insert into client(fullname,password,email,gender,age) values('{}','{}','{}','{}','{}')".format(d['fullname'],d['password'],d['email'],d['gender'],d['age']))
                connection.commit()
        else :
            cursor.execute("select email from client")
            email=cursor.fetchall()

            mail=d.get('email')
            passwd=d.get('password',0)
            print(passwd)
            print(mail)
            ls=[element for innerlist in email for element in innerlist]
            if mail in ls:
                cursor.execute("select password from client where email='{}'".format(d['email']))
                password=cursor.fetchone()
                print(passwd)
                if passwd==password[0]:
                    cursor.execute("select id,fullname from client where email='{}'".format(d['email']))
                    name=cursor.fetchone()
                    dt['name']=name[1]
                    dt['id']=name[0]
                    dt['cstatus']=True
                    dt['tstatus']=False
                    login=name[0]
                    print(name)
                    return redirect('/')
                else:
                    message='incorrect password'
                    
            else:
                message='user does not exists please signup'
                
    return render(request,"clientlogin.html",{'msg':message})
def trainerlogin(request):
    if request.method=='POST':
        message=''
        cursor=connection.cursor()
        d=request.POST
        print(d)
        if(len(d)>3):
            cursor.execute("select email from trainer")
            email=cursor.fetchall()
            ls=[element for innerlist in email for element in innerlist]
            mail=d.get('email')
            if mail in ls:
                message='user already exists please login'
                return render(request,'trainerlogin.html',{'msg':message})
            else:
                fname=d.get('fullname')
                passwd=d.get('password')
                price=d.get('price')
                gender=d.get('gender')
                print(passwd)
                cursor.execute("insert into trainer(fullname,password,email,gender,price) values('{}','{}','{}','{}',{})".format(fname,passwd,mail,gender,int(price)))
                connection.commit()
                cursor.execute("select id from trainer where email='{}'".format(mail))
                i=cursor.fetchone()
                cursor.execute("insert into avg_rating values({},{},{})".format(int(i[0]),0,0) )
                connection.commit()
        else :
            cursor.execute("select email from trainer")
            email=cursor.fetchall()
            ls=[element for innerlist in email for element in innerlist]
            print(ls)
            mail=d.get('email')
            passwd=d.get('password',0)
            if mail in ls:
                cursor.execute("select password from trainer where email='{}'".format(d['email']))
                password=cursor.fetchone()
                if passwd==password[0]:
                    cursor.execute("select id,fullname from trainer where email='{}'".format(d['email']))
                    name=cursor.fetchone()
                    dt['name']=name[1]
                    dt['id']=name[0]
                    dt['cstatus']=False
                    dt['tstatus']=True
                    return redirect('/')
                else:
                    message='incorrect password'
                    return render(request,'trainerlogin.html',{'msg':message})
            else:
                message='user does not exists please signup'
                return render(request,'trainerlogin.html',{'msg':message})
    return render(request,"trainerlogin.html")
def yourclients(request):
    cursor=connection.cursor()
    cursor.execute("select c.fullname,c.gender,c.age,c.email from client c,subscription s where c.id=s.cid and s.tid={}".format(dt['id']))
    clients=cursor.fetchall()
    clients_list=[]
    for i in clients:
        clients_list.append({'name':i[0],'gender':i[1],'age':i[2],'email':i[3]})
    
    print(clients_list)
    return render(request,'yourclients.html',{'dt':dt,'cl':clients_list})
def yourtrainer(request):
    rstatus=False
    sstatus=False
    tid=0
    cursor=connection.cursor()
    cursor.execute('select t.fullname,t.id from trainer t,subscription p where t.id=p.tid and p.cid={}'.format(dt['id']))
    ls=cursor.fetchall()
    print(ls)
    clients=[]
    trainer_list={}
    if len(ls)>=1:
        sstatus=True
        trainer_list['name']=ls[0][0]
        tid=ls[0][1]
        cursor.execute("select cid from client_rating")
        client_list=cursor.fetchall()
        cursor.execute("select rev_stars,count from avg_rating where id={}".format(tid))
        t=cursor.fetchall()
        trainer_list['rating']=t[0][0]
        trainer_list['count']=t[0][1]
        clients=[element for innerlist in client_list for element in innerlist]
    print(clients)
    if dt['id'] in clients:
        rstatus=True
    if request.method=='POST' and not rstatus:
        data=request.POST
        cursor.execute("insert into client_rating values({},{},{})".format(int(tid),dt['id'],int(request.POST.get('rate'))))
        connection.commit()
        rstatus=True
        return render(request,'yourtrainer.html',{'dt':dt,'trainer':trainer_list,'rstatus':rstatus,'sstatus':sstatus})
    return render(request,'yourtrainer.html',{'dt':dt,'trainer':trainer_list,'rstatus':rstatus,'sstatus':sstatus})
def logout(request):
    dt['id']=0
    dt['name']=''
    dt['tstatus']=False
    dt['cstatus']=False
    return redirect('/')