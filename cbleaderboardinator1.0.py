# -*- coding: utf-8 -*-
"""
Created on Sun Nov 23 22:11:57 2014

@author: yorick
"""
import urllib2
import lxml.etree as ET
import string
from collections import *
from Tkinter import *

Central=["White1", "BridgeA1", "BridgeA2", "BridgeB1", "BridgeB2"]
Dawn=["Dawn1", "Dawn2", "Dawn3", "Dawn4"]
Storm=["Storm1", "Storm2", "Storm3", "Storm4"]
Day=["Day1", "Day2", "Day3", "Day4"]
Night=["Night1", "Night2", "Night3", "Night4"]
Remix=["Stratos1", "Stratos2"]
Fog=["Temple1", "Temple2", "Temple3", "Temple4", "Temple5"]
Defiance=["Defiance1", "Defiance2", "Defiance3", "Defiance4", "Defiance5"]
Branches=[Central, Dawn, Storm, Day, Night, Remix, Fog, Defiance]
Names={"White1":"The Initial Entry","BridgeA1":"Beyond the Walls", "BridgeA2":"A Message","BridgeB1":"The Meaning",\
"BridgeB2":"No Excuse", "Dawn1":"Dreams","Dawn2":"The Clouds","Dawn3":"My Source","Dawn4":"My Inspiration",\
"Storm1":"A Window","Storm2":"Clarity","Storm3":"What's to Come","Storm4":"Redeployment","Day1":"Best Intentions",\
"Day2":"Escape","Day3":"Stability","Day4":"Acceptance","Night1":"Underneath","Night2":"In the Dark","Night3":"Emptiness",\
"Night4":"My Regrets","Stratos1":"Remix 1","Stratos2":"Remix 2","Temple1":"Ruins","Temple2":"To Dust","Temple3":"Doubt",\
"Temple4":"What Remains","Temple5":"Construction","Defiance1":"Desire","Defiance2":"Desperation","Defiance3":"Nostalgia",\
"Defiance4":"Expectations","Defiance5":"Chains"}

#Boring UI stuff
root = Tk()
root.minsize(400, 300)
root.attributes('-zoomed', False)
root.wm_title("Cloudbuilt Leaderboardinator 1.0")
cent=IntVar()
dawn=IntVar()
storm=IntVar()
day=IntVar()
night=IntVar()
remix=IntVar()
fog=IntVar()
defiance=IntVar()
status = StringVar()
hack = StringVar()


#Functionstuff
#Update status text
def StatusUpdate(str):
    status.set(str)
    root.update_idletasks()
    
#initiate xml parser, setting it to ignore invalid characters
parser = ET.XMLParser(recover=True, encoding='ascii')

#Load a page and parse it
def LoadPage(url, cleanup=False):
    Loaded=False
    while not Loaded:
        try:
            List=urllib2.urlopen(url, timeout=1)
            Loaded=True
        except Exception:
            Loaded=False 
    Liststr = List.read()
    if cleanup:
        #remove invalid tokens
        valid_chars = "-_.()/:[]<>?!=+-*\" %s%s" % (string.ascii_letters, string.digits)
        Liststr=''.join(c for c in Liststr if c in valid_chars)
    return ET.fromstring(Liststr, parser=parser)
    
#get the list of leaderboards
LBListData = LoadPage("http://steamcommunity.com/stats/262390/leaderboards/?xml=1", cleanup=True)

#Points for certain rank
def multiplier(i):
    if i==1:
        return 25
    elif(i<=20):
        return 22-i
    else: 
        return 0

#Produce Global leaderboards
def GlobalLeaderboards():
    Hackers=hack.get().strip().split(',')
    PlayerList=Counter()  
    Levels=[]
    f = file("leaderboardold","w")
    #Only analyse selected levels
    if cent.get()==1: 
        Levels+=Central
    if dawn.get()==1: 
        Levels+=Dawn
    if storm.get()==1: 
        Levels+=Storm
    if day.get()==1:
        Levels+=Day
    if night.get()==1:
        Levels+=Night
    if remix.get()==1:
        Levels+=Remix
    if fog.get()==1:
        Levels+=Fog
    if defiance.get()==1:
        Levels+=Defiance
    #Read leaderboard data
    for lb in LBListData.findall('leaderboard'):
        url=lb.find('url').text
        name=lb.find('name').text
        if (name.strip().endswith("Normal") and any([name.strip().startswith(stuff) for stuff in Levels ]) and "TEST"not in name):
            StatusUpdate("Analysing "+Names[name.strip().replace('Normal','')]+"...")
            i=1
            LBData=LoadPage(url)
            for entry in LBData.find('entries').findall('entry'):
                pid=entry.find('steamid').text
                if not any([pid==stuff for stuff in Hackers]):
                    PlayerList[pid]+=multiplier(i)
                    i+=1
                if i>20:
                    break
    i=1
    #Fetch Player names
    StatusUpdate("Fetching player names\n(might take a while)")
    for pid, score in PlayerList.most_common():
        PlayerData=LoadPage("http://steamcommunity.com/profiles/"+pid+"/?xml=1")
        name=PlayerData.find('steamID').text
        try:
            f.write(str(i)+' '+name+' '+str(score)+'  '+'\n')
        except:
            f.write(str(i)+' '+'Invalid Name'+' '+pid+str(score)+'  '+'\n')
        i+=1
    StatusUpdate("Done!")                     
    f.close()

#More boring GUI stuff
centralcheck = Checkbutton(root, text="Central section", anchor="w", variable=cent)
centralcheck.pack(fill=BOTH, expand=1)
dawncheck = Checkbutton(root, text="Dawn", anchor="w", variable=dawn)
dawncheck.pack(fill=BOTH, expand=1)
stormcheck = Checkbutton(root, text="Storm", anchor="w", variable=storm)
stormcheck.pack(fill=BOTH, expand=1)
daycheck = Checkbutton(root, text="Day", anchor="w", variable=day)
daycheck.pack(fill=BOTH, expand=1)
nightcheck = Checkbutton(root, text="Night", anchor="w", variable=night)
nightcheck.pack(fill=BOTH, expand=1)
remixcheck = Checkbutton(root, text="Remix", anchor="w", variable=remix)
remixcheck.pack(fill=BOTH, expand=1)
fogcheck = Checkbutton(root, text="Fog", anchor="w", variable=fog)
fogcheck.pack(fill=BOTH, expand=1)
defcheck = Checkbutton(root, text="Defiance", anchor="w", variable=defiance)
defcheck.pack(fill=BOTH, expand=1)
centralcheck.select()
dawncheck.select()
stormcheck.select()
daycheck.select()
nightcheck.select()
inf=Label(root, text="Hacker ID's separated\nby comma's")
inf.pack(fill=BOTH, expand=1)
e = Entry(root, textvariable=hack)
e.pack(fill=BOTH, expand=1)
st=Label(root, textvariable=status)
st.pack(fill=BOTH, expand=1)
status.set("Idle...")
startb = Button(root, text='Start!', anchor="w", command=GlobalLeaderboards)
startb.pack(fill=BOTH, expand=1)               


root.mainloop()





''' test function, for later use
for lb in LBListData.findall('leaderboard'):
    url=lb.find('url').text
    name=lb.find('name').text
    if name.strip()=="Temple1UnlimitedEnergy":
        LB=urllib2.urlopen(url)
        LBstr=LB.read()
        LBData=ET.fromstring(LBstr, parser=parser)
        for entry in LBData.find('entries').findall('entry'):
            rank=entry.find('rank').text
            pid=entry.find('steamid').text
            print("http://steamcommunity.com/profiles/"+pid+"/?xml=1")
            Player=urllib2.urlopen("http://steamcommunity.com/profiles/"+pid+"/?xml=1")
            Playerstr=Player.read()
            PlayerData=ET.fromstring(Playerstr, parser=parser)
            name=PlayerData.find('steamID').text
            try:
                f.write(rank+' '+name+'\n')
            except:
                pass
                
''' 
