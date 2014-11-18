# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 18:08:29 2014

@author: arichi
"""

import numpy as np
import matplotlib.pylab as plt
import string
import cPickle as pickle
import os

#os.chdir('exploreneuraldata/problem_set2')

def init_game(nl):

    if nl=="new" or nl=="clear":
        wh=[]
        whx=[]
        why=[]
        whhx=[]
        whhy=[]

        bk=[]
        bkx=[]
        bky=[]
        bkhx=[]
        bkhy=[]
        
        turn=0
        bkcnt=0
        whcnt=0
        
        goban=int(raw_input("Please enter the size of the field \n"))
        komi=0.5
        
    elif nl=="load":
        f = open('kamiken_save.pickle','r')
        wh=pickle.load(f)
        whx=pickle.load(f)
        why=pickle.load(f)
        whhx=pickle.load(f)
        whhy=pickle.load(f)
        bk=pickle.load(f)
        bkx=pickle.load(f)
        bky=pickle.load(f)
        bkhx=pickle.load(f)
        bkhy=pickle.load(f)
        goban=pickle.load(f)
        komi=pickle.load(f)
        turn=pickle.load(f)
        bkcnt=pickle.load(f)
        whcnt=pickle.load(f)
        f.close()      
    
    else:
        init_game(raw_input("try again\n"))
    
    if nl=="clear":
        os.remove('kamiken_save.pickle')
    
    return wh,whx,why,whhx,whhy,bk,bkx,bky,bkhx,bkhy,goban,komi,turn,bkcnt,whcnt


def save_game(wh,whx,why,whhx,whhy,bk,bkx,bky,bkhx,bkhy,goban,komi,turn,bkcnt,whcnt):
    
    os.remove('kamiken_save.pickle')

    f = open('kamiken_save.pickle','w')
    pickle.dump(wh,f)
    pickle.dump(whx,f)
    pickle.dump(why,f)
    pickle.dump(whhx,f)
    pickle.dump(whhy,f)
    pickle.dump(bk,f)
    pickle.dump(bkx,f)
    pickle.dump(bky,f)
    pickle.dump(bkhx,f)
    pickle.dump(bkhy,f)
    pickle.dump(goban,f)
    pickle.dump(komi,f)
    pickle.dump(turn,f)
    pickle.dump(bkcnt,f)
    pickle.dump(whcnt,f)
    f.close()
    
    print "Game successfully saved to kamien_save.pickle \n"


def unique_rows(data):
    uniq = np.unique(data.view(data.dtype.descr * data.shape[1]))
    return uniq.view(data.dtype).reshape(-1, data.shape[1])


def unique_cols(data):
    uniq = np.unique(data.view(data.dtype.descr * data.shape[0]))
    return uniq.view(data.dtype).reshape(-1, data.shape[0])    


def draw_field(bkx,bky,whx,why,bkhx,bkhy,whhx,whhy,goban):

    xtcks=list(np.array(range(0,goban))+0.5)
    ytcks=list(np.array(range(0,goban+1))-0.5)
    fig=plt.figure()
    field=fig.add_subplot(111)
    plt.scatter(bkhx,bkhy,c='blue',s=50)
    plt.scatter(whhx,whhy,c='red',s=50)
    plt.scatter(bkx,bky,c='black',s=300)
    plt.scatter(whx,why,c='grey',s=300)
    plt.grid()
    plt.xlim(0,goban)
    plt.ylim(0,goban)
    plt.yticks(range(0,goban))
    plt.xticks(np.array(range(0,goban)),alphabetU)
    field.set_xticklabels([])
    field.set_yticklabels([])
    field.xaxis.set_minor_locator(plt.FixedLocator(xtcks))
    field.xaxis.set_minor_formatter(plt.FixedFormatter(alphabetU))
    field.yaxis.set_minor_locator(plt.FixedLocator(ytcks))
    field.yaxis.set_minor_formatter(plt.FixedFormatter(range(0,goban+1)))
    plt.tick_params(axis="x",which="minor",bottom="on",top="on")
    plt.show()
    

def make_turn(crd,crdx,crdy,cnt,turn):

    if turn%2==0:              # since blacks start, every even turn is theirs
        print "Black's turn",
    if turn%2!=0:
        print "White's turn",
    
    crd.append(raw_input("Where do you want to place a stone?\n"))  # raw input of the square to put ishi in
        # split it into x and y axis values
    if crd[-1]=="SKIP" or crd[-1]=="skip" or crd[-1]=="pass" or \
        crd[-1]=="PASS":      # NOT WORKING (god knows why)
        crd.remove(crd[-1])
        return crdx, crdy, "skip","running"
    if crd[-1]=="STOP" or crd[-1]=="stop" or crd[-1]=="s"  or crd[-1]=="end":
        return crdx, crdy, "skip","stop"
    if crd[-1]=="save" or crd[-1]=="SAVE":
        crd.remove(crd[-1])
        return crdx, crdy, "skip", "save"
    if crd[-1]=="quit" or crd[-1]=="exit":
        crd.remove(crd[-1])
        return crdx,crdy,"skip","quit"
    crdx.append(alphabetL.index(crd[cnt][0])+0.5) # add/subtract  0.5 to 
    crdy.append(int(crd[cnt][1:])-0.5)   # place t in the middle    pass
    
    return crdx,crdy,"","running"
    

def make_hits(crdx,crdy,crdhx,crdhy,cnt,turn,skip):
    
    if skip=="skip":
        return crdhx,crdhy,cnt    
            # 4 x axis positions of markers
    crdhx.append(crdx[cnt])
    crdhx.append(crdx[cnt])
    crdhx.append(crdx[cnt]-1)
    crdhx.append(crdx[cnt]+1)
        
        # 4 y axis positions for respective x axis positions
    if turn%2==0: 
        crdhy.append(crdy[cnt]+0.9)
        crdhy.append(crdy[cnt]-1.1)
        crdhy.append(crdy[cnt]-0.1)        
        crdhy.append(crdy[cnt]-0.1)   
    if turn%2!=0:
        crdhy.append(crdy[cnt]+1.1)
        crdhy.append(crdy[cnt]-0.9)
        crdhy.append(crdy[cnt]+0.1)        
        crdhy.append(crdy[cnt]+0.1)           
       
    cnt+=1            # personal turn counter   
    
    return crdhx,crdhy,cnt


def count_hits(bkhx,bkhy,whhx,whhy,goban,komi):

    bkhx=np.array(bkhx)
    bkhy=np.array(bkhy)
    a=bkhx>0
    b=bkhx<goban
    c=bkhy>0
    d=bkhy<goban
    ind=a&b&c&d
    bkhx=bkhx[ind]
    bkhy=bkhy[ind]
    
    whhx=np.array(whhx)
    whhy=np.array(whhy)
    a=whhx>0
    b=whhx<goban
    c=whhy>0
    d=whhy<goban
    ind=a&b&c&d
    whhx=whhx[ind]
    whhy=whhy[ind]

    bkhts=np.vstack((bkhx,bkhy))
    bkhts=0.5*np.round(2*bkhts)
    bkhts=bkhts[:,np.argsort(bkhts[0])]
#    bkhts=unique_rows(bkhts.T).T   
    bkhts=unique_cols(bkhts)     
     
    whhts=np.vstack((whhx,whhy))
    whhts=0.5*np.round(2*whhts)
    whhts=whhts[:,np.argsort(whhts[0])]
#    whhts=unique_rows(whhts.T).T
    whhts=unique_cols(whhts)    
    
    scorew=len(whhts[:,0])
    scoreb=len(bkhts[:,0])+komi
    
    a=whhts[:,0]
    b=whhts[:,1]
    c=bkhts[:,0]
    d=bkhts[:,1]
    aa=np.hstack((a,c))
    bb=np.hstack((b,d))
    tot=np.vstack((aa,bb))
    l1=len(tot[0,:])
    tot_u=tot[:,np.argsort(tot[0])]
    tot_u=unique_cols(tot_u)
    l2=len(tot_u[:,0])
        
    scorew-=l1-l2
    scoreb-=l1-l2
          
    return scoreb,scorew

# field size NxN
#goban=int(raw_input("Please the size of the field \n"))

alphabetU=list(string.ascii_uppercase)
alphabetL=list(string.ascii_lowercase)

# Show initial emtpy field or previously saved
wh,whx,why,whhx,whhy,bk,bkx,bky,bkhx,bkhy,goban,komi,turn,bkcnt,whcnt=init_game(raw_input("'new' or 'load'?'\n"))
draw_field(bkx,bky,whx,why,bkhx,bkhy,whhx,whhy,goban)









game="running"

while game=="running":

        # Start of the turn

    if turn%2==0:              # since blacks start, every even turn is theirs
        bkx,bky,skip,game=make_turn(bk,bkx,bky,bkcnt,turn)
        bkhx,bkhy,bkcnt=make_hits(bkx,bky,bkhx,bkhy,bkcnt,turn,skip)
        skip=""
        if game=="save":
            save_game(wh,whx,why,whhx,whhy,bk,bkx,bky,bkhx,bkhy,goban,komi,turn,bkcnt,whcnt)
            game="running"
            continue


    if turn%2!=0:            # similarly, odd turns are white's.
        whx,why,skip,game=make_turn(wh,whx,why,whcnt,turn)
        whhx,whhy,whcnt=make_hits(whx,why,whhx,whhy,whcnt,turn,skip)    
        skip=""            
        if game=="save":
            save_game(wh,whx,why,whhx,whhy,bk,bkx,bky,bkhx,bkhy,goban,komi,turn,bkcnt,whcnt)
            game="running"
            continue
                ##### Goban at the end of a turn #####
    if game=="running":
        draw_field(bkx,bky,whx,why,bkhx,bkhy,whhx,whhy,goban)
    
    if turn>0 and turn%10==0: # autosave every 10 turns
        save_game(wh,whx,why,whhx,whhy,bk,bkx,bky,bkhx,bkhy,goban,komi,turn,bkcnt,whcnt)
    
    turn+=1

if game=="stop":
    draw_field(bkx,bky,whx,why,bkhx,bkhy,whhx,whhy,goban)
    bksc,whsc=count_hits(bkhx,bkhy,whhx,whhy,goban,komi)

    print "White's score is "+str(whsc)+" points"+"\n"+"Blacks's score is "+\
        str(bksc)+" points"
if game=="quit":
    print "まったね！"