#!/bin/python2.5

"""
This file is part of the web2py Web Framework (Copyrighted, 2007-2008)
Developed in Python by Massimo Di Pierro <mdipierro@cs.depaul.edu>
"""

import sys, cStringIO

if sys.version[:3]!='2.5':
    sys.stderr.write('web2py requires Python 2.5 but you are running:\n%s' % sys.version)
    sys.exit(1)

ProgramName="web2py Enterprise Framework"
ProgramAuthor='Created by Massimo Di Pierro, Copyright 2007-2008'
ProgramVersion=open('VERSION','r').read().strip()

class IO:
    def __init__(self):
        self.buffer=cStringIO.StringIO()
    def write(self,data):
        sys.__stdout__.write(data)       
        if hasattr(self,'callback'): self.callback(data)
        else: self.buffer.write(data)

try: 
    import tkMessageBox, Tkinter
    havetk=True
except:
    havetk=False
    
print ProgramName
print ProgramAuthor
print ProgramVersion

from gluon.main import HttpServer, save_password
from gluon.fileutils import tar, untar
from optparse import *
import time, webbrowser, thread, re, cStringIO, os, stat, socket

def try_start_browser(url):
    try: webbrowser.open(url)
    except: print 'warning: unable to detect your browser'

def start_browser(ip,port):
    print 'please visit:'
    print '\thttp://%s:%s/welcome' % (ip,port)
    print 'starting browser...in 5 seconds'
    time.sleep(5)
    try_start_browser('http://%s:%s/welcome'%(ip,port))

def presentation(root):
        root.withdraw()
        dx=root.winfo_screenwidth()
        dy=root.winfo_screenheight()
        dialog=Tkinter.Toplevel(root)
        dialog.geometry('%ix%i+%i+%i' % (400,300,dx/2-200, dy/2-150))
        dialog.overrideredirect(1)
        dialog.focus_force()
        canvas=Tkinter.Canvas(dialog, background='white', width=400, height=300)
        canvas.pack()      
        root.update()  
        for counter in range(5):            
            if counter is 0:
                canvas.create_text(200,50, text='Welcome to ...',
                                        font=('Helvetica',12),
                                        anchor=Tkinter.CENTER, fill='#195866')
            elif counter is 1:
               canvas.create_text(200,130, text=ProgramName,
                                        font=('Helvetica',18),
                                        anchor=Tkinter.CENTER, fill='#FF5C1F')
            elif counter is 2:
                canvas.create_text(200,170,
                                        text=ProgramAuthor,
                                        font=('Helvetica',12),
                                        anchor=Tkinter.CENTER, fill='#195866')
            elif counter is 3:
                canvas.create_text(200,250, text=ProgramVersion,
                                        font=('Helvetica',12),
                                        anchor=Tkinter.CENTER, fill='#195866')
            else:
                dialog.destroy()
                return
            root.update()
            time.sleep(1.5)
        return root

class web2pyDialog:
    def __init__(self,root):
        root.title('web2py server')
        self.root=Tkinter.Toplevel(root)
        self.menu=Tkinter.Menu(self.root)

        servermenu = Tkinter.Menu(self.menu,tearoff=0)
        httplog=os.path.join(os.getcwd(),'httpserver.log')
        servermenu.add_command(label='View httpserver.log', command=lambda:try_start_browser(httplog))
        servermenu.add_command(label='Quit (pid:%i)' % os.getpid(), command=self.quit)
        self.menu.add_cascade(label="Server", menu=servermenu)

        self.pagesmenu = Tkinter.Menu(self.menu,tearoff=0)  
        self.menu.add_cascade(label="Pages", menu=self.pagesmenu)

        helpmenu = Tkinter.Menu(self.menu,tearoff=0)
        helpmenu.add_command(label="Home Page", command=lambda: try_start_browser('http://www.web2py.com'))
        helpmenu.add_command(label="About", command=lambda:tkMessageBox.showinfo('About web2py','%s\n%s\n%s'%(ProgramName,ProgramAuthor,ProgramVersion)))
        self.menu.add_cascade(label="Info", menu=helpmenu)

        self.root.config(menu=self.menu)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)
        sticky=Tkinter.NW
        Tkinter.Label(self.root, text="Choose a password:",justify=Tkinter.LEFT).grid(row=0,column=0,sticky=sticky)
        self.password = Tkinter.Entry(self.root,show='*')
        self.password.grid(row=0, column=1,sticky=sticky)
        Tkinter.Label(self.root, text="Running from host:",justify=Tkinter.LEFT).grid(row=1,column=0,sticky=sticky)
        self.ip = Tkinter.Entry(self.root)
        self.ip.insert(Tkinter.END,'127.0.0.1')
        self.ip.grid(row=1, column=1,sticky=sticky)
        Tkinter.Label(self.root, text="Running from port:",justify=Tkinter.LEFT).grid(row=2,column=0,sticky=sticky)
        self.port_number = Tkinter.Entry(self.root)
        self.port_number.insert(Tkinter.END,'8000')
        self.port_number.grid(row=2, column=1,sticky=sticky)
        self.canvas=Tkinter.Canvas(self.root,width=300,height=100,bg='black')
        self.canvas.grid(row=3,column=0,columnspan=2)
        self.canvas.after(1000,self.update_canvas)
        frame=Tkinter.Frame(self.root)
        frame.grid(row=4,column=0,columnspan=2)
        self.button_start=Tkinter.Button(frame,text='start server',command=self.start)
        self.button_start.grid(row=0, column=0)
        self.button_stop=Tkinter.Button(frame,text='stop server',command=self.stop)
        self.button_stop.grid(row=0, column=1)
        self.button_stop.configure(state='disabled')

    def update(self,text):
        try:
            self.text.configure(state='normal')
            self.text.insert('end',text)
            self.text.configure(state='disabled')
        except: pass ### this should only happen in case app is destroyed
    def connect_pages(self):
        for file in os.listdir('applications/'):
            if os.access('applications/%s/__init__.py' % file,os.R_OK):
                url=self.url+'/'+file
                self.pagesmenu.add_command(label=url, command=lambda u=url:try_start_browser(u))
    def quit(self):
        self.server.stop()
        self.root.destroy()
        sys.exit()
    def error(self,message):
        tkMessageBox.showerror("web2py start server",message)
        return
    def start(self):         
        password=self.password.get()
        if not password:
            self.error('no password, no web admin interface')
        ip=self.ip.get()
        if ip and not re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}').match(ip):
            return self.error('invalid host ip address')
        try: port=int(self.port_number.get())
        except: 
            return self.error('invalid port number')
        self.url='http://%s:%s' % (ip,port)
        self.connect_pages()
        self.button_start.configure(state='disabled')
        try:
            self.server=HttpServer(ip,port,password)        
            thread.start_new_thread(self.server.start,())            
        except Exception, e:
            self.button_start.configure(state='normal')
            return self.error(str(e))
        self.button_stop.configure(state='normal')
        thread.start_new_thread(start_browser,(ip,port))
        self.password.configure(state='readonly')
        self.ip.configure(state='readonly')
        self.port_number.configure(state='readonly')
    def stop(self):
        self.button_start.configure(state='normal')
        self.button_stop.configure(state='disabled')
        self.password.configure(state='normal')
        self.ip.configure(state='normal')
        self.port_number.configure(state='normal')
        self.server.stop()
    def update_canvas(self):
        try:
            t1=os.stat('httpserver.log')[stat.ST_SIZE]
        except IOError:
            self.canvas.after(1000, self.update_canvas ) 
            return
        try:
            file=open('httpserver.log','r')
            file.seek(self.t0)
            data=file.read(t1-self.t0)
            self.p0=self.p0[1:]+[1+98/(1+data.count('\n'))]
            for i in range(len(self.p0)-1):
                c=self.canvas.coords(self.q0[i])
                self.canvas.coords(self.q0[i],
                                   (c[0],self.p0[i],c[2],self.p0[i+1]))
            self.t0=t1
        except Exception, e:
            self.t0=time.time()
            self.t0=t1
            self.p0=[0]*300
            self.q0=[self.canvas.create_line(i,99,i+1,99,fill='green') for i in range(len(self.p0))]
        self.canvas.after(1000, self.update_canvas ) 

def console():
    usage="""python web2py.py"""
    description="""web2py Web Framework startup script. ATTENTION: unless a password is specified (-a 'passwd')  web2py will attempt to run a GUI. In this case command line options are ignored."""
    parser=OptionParser(usage,None,Option,ProgramVersion)
    parser.description=description
    parser.add_option('-i','--ip',default='127.0.0.1',dest='ip',
                  help='the ip address of the server (127.0.0.1)')
    parser.add_option('-p','--port',default='8000',dest='port',
                  help='the port for of server (8000)')
    parser.add_option('-a','--password',default='<ask>',dest='password',
                  help='the password to be used for administration'+\
                       "(use -a '<recycle>' to reuse the last password)")
    parser.add_option('-u','--upgrade',default='no',dest='upgrade',
                  help='upgrade applications')
    parser.add_option('-c','--ssl_certificate',default='',
                  dest='ssl_certificate',
                  help='file that contains ssl certificate')
    parser.add_option('-k','--ssl_private_key',default='',
                  dest='ssl_private_key',
                  help='file that contains ssl private key')
    parser.add_option('-d','--pid_filename',default='httpserver.pid',
                  dest='pid_filename',
                  help='file where to store the pid of the server')
    parser.add_option('-l','--log_filename',default='httpserver.log',
                  dest='log_filename',
                  help='file where to log connections')
    parser.add_option('-s','--server_name',default=socket.gethostname(),
                  dest='server_name',
                  help='the server name for the web server')

    (options, args) = parser.parse_args()
    if not os.access('applications', os.F_OK):
        os.mkdir('applications')
    if not os.access('applications/admin', os.F_OK):
        os.mkdir('applications/admin')
    if not os.access('applications/welcome', os.F_OK):
        os.mkdir('applications/welcome')
    if not os.access('applications/examples', os.F_OK):
        os.mkdir('applications/examples')
    if not os.access('deposit', os.F_OK):
        os.mkdir('deposit')
    if not os.access('applications/__init__.py',os.F_OK) or options.upgrade=='yes':
        print 'unpacking apps, this may take a few minutes...'
        untar('admin.tar','applications/admin/')
        untar('welcome.tar','applications/welcome/')
        untar('examples.tar','applications/examples/')
        open('applications/__init__.py','w').write('')
        print 'default applications are now installed'    
    else:
        print 'default applications appear to be installed already'
    return options

def start():
    options=console()
    root=None
    if options.password=='<ask>' and havetk:
       try: root=Tkinter.Tk()
       except: pass
    if root:
       root.focus_force()
       presentation(root)
       master=web2pyDialog(root)
       try: root.mainloop()
       except: master.quit()
       sys.exit()
    if not root and options.password=='<ask>':
       options.password=raw_input('choose a password:')
    if not options.password: 
       print 'no password, no admin interface'
    ip,port=options.ip,int(options.port)
    print 'please visit:'
    print '\thttp://%s:%s/welcome' % (ip,port)
    print 'use "kill -SIGTERM %i" to shutdown the web2py server'  % os.getpid()
    server=HttpServer(ip=ip,port=port,password=options.password,
                      pid_filename=options.pid_filename,
                      log_filename=options.log_filename,
                      ssl_certificate=options.ssl_certificate,
                      ssl_private_key=options.ssl_private_key,
                      server_name=options.server_name)
    try: server.start()
    except KeyboardInterrupt: server.stop()