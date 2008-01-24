"""
This file is part of web2py Web Framework (Copyrighted, 2007)
Developed by Massimo Di Pierro <mdipierro@cs.depaul.edu>
License: GPL v2
"""

import sys, os, re, cgi
from fileutils import listdir

__all__=['translator','findT','update_all_languages']

# pattern to find T(bla bla bla) expressions
regex_translate=re.compile("""[^\w.]T\((?P<name>(?:(?:["][^"]+["])|(?:[\'][^\']+[\'])))\)""")

# patter for a valid accept_language
regex_language=re.compile('[a-zA-Z]{2}(\-[a-zA-Z]{2})?(\-[a-zA-Z]+)?')

class lazyT:
    """ 
    never to be called explicitly, returned by translator.__call__ 
    """
    def __init__(self,message,symbols={},self_t=None):
        self.m=message
        self.s=symbols
        self.t=self_t
    def __str__(self):
        if self.t and self.t.has_key(self.m): return self.t[self.m] % self.s
        return self.m % self.s
    def xml(self):
        return cgi.esacpe(str(self))

class translator:
    """ 
    this class is intantiated once in gluon/main.py as the T object 

    T.force(None) # turns off translation
    T.force('fr, it') # forces web2py to translate using fr.py or it.py

    T("Hello World") # translates "Hello World" using the selected file

    notice 1: there is no need to force since, by default, T uses accept_langauge
    to determine a translation file. 

    notice 2: en and en-en are considered different languages!
    """
    def __init__(self,request):        
        self.folder=request.folder
        self.current_languages=[]
        self.force(languages=request.env.http_accept_language)
    def force(self,languages=None):
        if languages:
            if isinstance(languages,(str,unicode)):
                accept_languages=languages.split(';')
                languages=[]
                for al in accept_languages: languages+=al.split(',')
            for language in languages:
                language=language.strip()
                if language in self.current_languages: break
                if not regex_language.match(language): continue
                filename=os.path.join(self.folder,'languages/','%s.py'%language)
                if os.access(filename,os.R_OK):
                    self.accepted_language=language
                    self.t=eval(open(filename,'r').read())
                    return
        self.t=None ### no langauge by default
    def __call__(self,message,symbols={}):
        return lazyT(message,symbols,self.t)
            
def findT(application,language='en-us'):
    """ 
    must be run by the admin app 
    """
    path=os.path.join('applications/',application)
    try:
        sentences=eval(open(os.path.join(path,'languages/','%s.py' % language),'r').read())
    except:
        sentences={}
    for file in listdir(path,'.+',0):        
        data=open(file,'r').read()
        items=regex_translate.findall(data)        
        for item in items:
            msg=item[1:-1]
            if item and not sentences.has_key(msg):
                sentences[msg]=''
    keys=sentences.keys()
    keys.sort()
    file=open(os.path.join(path,'languages/','%s.py' % language),'w')
    file.write('{\n')
    for key in keys:
        file.write("%s:%s,\n" % (repr(str(key)),repr(str(sentences[key]))))
    file.write('}\n')
    file.close()

def update_all_languages(application):
    path='applications/%s/languages/' % application
    for language in  listdir(path,'.+'):
        findT(application,language[:-3])