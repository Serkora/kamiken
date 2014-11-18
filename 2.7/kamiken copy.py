# -*- coding: utf-8 -*-
"""
Created on Fri Oct  3 18:08:29 2014

@author: arichi
"""

import numpy as np
import matplotlib.pylab as plt
import string

#os.chdir('exploreneuraldata/problem_set2')


wh=[]
whx=[]
why=[]
whhx=[]
whhy=[]
whcnt=0

bk=[]
bkx=[]
bky=[]
bkhx=[]
bkhy=[]
bkcnt=0

# field size NxN
#goban=int(raw_input("Please the size of the field \n"))
goban=5

alphabetU=list(string.ascii_uppercase)
alphabetL=list(string.ascii_lowercase)
xtcks=list(np.array(range(0,goban))+0.5)
ytcks=list(np.array(range(0,goban+1))-0.5)



def draw_field(bkx,bky,whx,why,bkhx,bkhy,whhx,whhy):
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
    



# Show initial emtpy field or previously saved
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


turn=0



    


for i in range(0,1):

        # Start of the turn

                    ##### Stone placement #####

    if turn%2==0:              # since blacks start, every even turn is theirs
        print "Black's turn"
        bk.append(raw_input())  # raw input of the square to put ishi in
            # split it into x and y axis values
        if bk[-1]=="SKIP" or bk[-1]=="skip" or bk[-1]=="pass" or \
            bk[-1]=="PASS":      # NOT WORKING (god knows why)
            bk.remove(bk[-1])
            continue
        if bk[-1]=="STOP" or bk[-1]=="stop" or bk[-1]=="s"  or bk[-1]=="end":
            break
        if bk[-1]=="save" or bk[-1]=="SAVE":
            bk.remove(bk[-1])
            # to be added later
        bkx.append(alphabetL.index(bk[bkcnt][0])+0.5) # add/subtract  0.5 to 
        bky.append(int(bk[bkcnt][1:])-0.5)   # place t in the middle


    elif turn%2!=0:            # similarly, odd turns are white's.
        print "White's turn"
        wh.append(raw_input())
        if wh[-1]=="SKIP" or wh[-1]=="skip" or wh[-1]=="pass" or \
            wh[-1]=="PASS":      # NOT WORKING (god knows why)
            wh.remove(wh[-1])
            continue
        if wh[-1]=="STOP" or wh[-1]=="stop" or wh[-1]=="s"  or wh[-1]=="end":
            break
        if wh[-1]=="save" or wh[-1]=="SAVE":
            wh.remove(wh[-1])
            # to be added later
        whx.append(alphabetL.index(wh[whcnt][0])+0.5)
        why.append(int(wh[whcnt][1:])-0.5)
                
    
                    ##### "Hit" squares calculation #####
    
        # for blacks
    if turn%2==0:

        # 4 x axis positions of markers
        bkhx.append(bkx[bkcnt])
        bkhx.append(bkx[bkcnt])
        bkhx.append(bkx[bkcnt]-1)
        bkhx.append(bkx[bkcnt]+1)
        
        # 4 y axis positions for respective x axis positions
    
        bkhy.append(bky[bkcnt]+0.9)
        bkhy.append(bky[bkcnt]-1.1)
        bkhy.append(bky[bkcnt]-0.1)        
        bkhy.append(bky[bkcnt]-0.1)     
       
        bkcnt+=1            # personal turn counter   
        
        # for whites
    if turn%2!=0:

        # 4 x axis positions of markers
        whhx.append(whx[whcnt])
        whhx.append(whx[whcnt])
        whhx.append(whx[whcnt]-1)
        whhx.append(whx[whcnt]+1)
        
        # 4 y axis positions for respective x axis positions
    
        whhy.append(why[whcnt]+1.1)
        whhy.append(why[whcnt]-0.9)
        whhy.append(why[whcnt]+0.1)        
        whhy.append(why[whcnt]+0.1)

        whcnt+=1    
    
                ##### Goban at the end of a turn #####

    
    # next turn
    turn+=1