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
import ttk

Central=["White1", "BridgeA1", "BridgeA2", "BridgeB1", "BridgeB2"]
Dawn=["Dawn1", "Dawn2", "Dawn3", "Dawn4"]
Storm=["Storm1", "Storm2", "Storm3", "Storm4"]
Day=["Day1", "Day2", "Day3", "Day4"]
Night=["Night1", "Night2", "Night3", "Night4"]
Remix=["Stratos1", "Stratos2", "Stratos3", "FogRemix1", "DefianceRemix1"]
Fog=["Temple1", "Temple2", "Temple3", "Temple4", "Temple5"]
Defiance=["Defiance1", "Defiance2", "Defiance3", "Defiance4", "Defiance5"]
Branches=[Central, Dawn, Storm, Day, Night, Remix, Fog, Defiance]
Names={"White1":"The Initial Entry","BridgeA1":"Beyond the Walls", "BridgeA2":"A Message","BridgeB1":"The Meaning",\
"BridgeB2":"No Excuse", "Dawn1":"Dreams","Dawn2":"The Clouds","Dawn3":"My Source","Dawn4":"My Inspiration",\
"Storm1":"A Window","Storm2":"Clarity","Storm3":"What's to Come","Storm4":"Redeployment","Day1":"Best Intentions",\
"Day2":"Escape","Day3":"Stability","Day4":"Acceptance","Night1":"Underneath","Night2":"In the Dark","Night3":"Emptiness",\
"Night4":"My Regrets","Stratos1":"Remix 1","Stratos2":"Remix 2","Stratos3":"Remix 3","FogRemix1":"Fog Remix",\
"DefianceRemix1":"Defiance Remix","Temple1":"Ruins","Temple2":"To Dust","Temple3":"Doubt",\
"Temple4":"What Remains","Temple5":"Construction","Defiance1":"Desire","Defiance2":"Desperation","Defiance3":"Nostalgia",\
"Defiance4":"Expectations","Defiance5":"Chains"}

#Boring UI stuff
root = Tk()
root.minsize(500, 300)
root.wm_title("Cloudbuilt Leaderboardinator 2.0")
cent=IntVar()
dawn=IntVar()
storm=IntVar()
day=IntVar()
night=IntVar()
remix=IntVar()
fog=IntVar()
defiance=IntVar()
status = StringVar()
status2 = StringVar()
hack = StringVar()
num = StringVar()
num2 = StringVar()
MULT = 1000000


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
    
#Get player score for level
#returns None if no score is found (player didn't play level)
def GetPlayerLevelScore(url, stid):
    url+="&steamid="
    url+=stid.strip()
    page=LoadPage(url)
    score=None
    '''taking the right score because Steam is dumb and gives a list of
    steamid's that are more or less right, because reasons'''
    for entry in page.find('entries').findall('entry'):
        if entry.find('steamid').text==stid:
            score=entry.find('score')
            break
    if score!=None:
        score=int(score.text)
    return score
    
    
'''http://steamcommunity.com/stats/262390/leaderboards/282463/?xml=1&steamid=76561198063493260'''
#get the list of leaderboards
LBListData = LoadPage("http://steamcommunity.com/stats/262390/leaderboards/?xml=1", cleanup=True)

def GetLevels():
    Levels=[]
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
    return Levels

#Produce a dictionary of leaderboard names and url's
def GetLeaderboardURL(Levels):
    leaderboards={}
    for lb in LBListData.findall('leaderboard'):
        url=lb.find('url').text
        name=lb.find('name').text
        if (name.strip().endswith("Normal") and any([name.strip().startswith(stuff) for stuff in Levels ]) and "TEST"not in name):
            leaderboards[name]=url
    return leaderboards
    
#Produce total player score
def GetPlayerScore(stid, display=False):
    Levels=GetLevels()
    leaderboards=GetLeaderboardURL(Levels)
    totScore=0
    if display:
        status2.set("Calculating...")
        root.update_idletasks()
    for name, url in leaderboards.iteritems():  
        score=GetPlayerLevelScore(url,stid)
        if score!=None:
            totScore+=MULT-score
    if display:
        status2.set("Score = "+str(totScore))
        root.update_idletasks()
    return totScore 
    
#Produce Global leaderboards
def GlobalLeaderboards():
    n=int(num.get().strip())
    Hackers=hack.get().strip().split(',')
    PlayerList=Counter()  
    Levels=GetLevels()
    f = file("leaderboard.txt","w")
    leaderboards=GetLeaderboardURL(Levels)
    #Read leaderboard data and fetch players
    for name, url in leaderboards.iteritems(): 
        StatusUpdate("Analysing "+Names[name.strip().replace('Normal','')]+"...")
        i=1
        LBData=LoadPage(url)
        for entry in LBData.find('entries').findall('entry'):
            pid=entry.find('steamid').text
            if not any([pid==stuff for stuff in Hackers]):
                PlayerList[pid]=1
                i+=1
            if i>2*n:
                break
    #Read leaderboard data and fetch scores     
    for pid in PlayerList:
        StatusUpdate("Calculating scores for "+pid+"...")
        PlayerList[pid]=GetPlayerScore(pid)
     
    #Fetch Player names
    i=1
    StatusUpdate("Fetching player names\n(might take a while)")
    for pid, score in PlayerList.most_common():
        PlayerData=LoadPage("http://steamcommunity.com/profiles/"+pid+"/?xml=1")
        name=PlayerData.find('steamID').text
        #try:
        try:
            f.write(str(i)+' '+name+' '+str(score)+'  '+'\n')
        except:
            f.write(str(i)+' '+'Invalid Name'+' '+pid+str(score)+'  '+'\n')
        i+=1
        if i>n:
            break
    StatusUpdate("Done!")                     
    f.close()


#More boring GUI stuff
window = ttk.Panedwindow(root, orient=HORIZONTAL)
window.pack(fill=BOTH, expand=1)

f1 = ttk.Labelframe(window, text='Levels', width=100, height=100)
f2 = ttk.Labelframe(window, text='Function', width=100, height=100); # second pane
window.add(f1)
window.add(f2)
# first pane, level selection:
centralcheck = Checkbutton(f1, text="Central section", anchor="w", variable=cent)
centralcheck.pack(fill=BOTH, expand=1)
dawncheck = Checkbutton(f1, text="Dawn", anchor="w", variable=dawn)
dawncheck.pack(fill=BOTH, expand=1)
stormcheck = Checkbutton(f1, text="Storm", anchor="w", variable=storm)
stormcheck.pack(fill=BOTH, expand=1)
daycheck = Checkbutton(f1, text="Day", anchor="w", variable=day)
daycheck.pack(fill=BOTH, expand=1)
nightcheck = Checkbutton(f1, text="Night", anchor="w", variable=night)
nightcheck.pack(fill=BOTH, expand=1)
remixcheck = Checkbutton(f1, text="Remix", anchor="w", variable=remix)
remixcheck.pack(fill=BOTH, expand=1)
fogcheck = Checkbutton(f1, text="Fog", anchor="w", variable=fog)
fogcheck.pack(fill=BOTH, expand=1)
defcheck = Checkbutton(f1, text="Defiance", anchor="w", variable=defiance)
defcheck.pack(fill=BOTH, expand=1)
centralcheck.select()
dawncheck.select()
stormcheck.select()
daycheck.select()
nightcheck.select()
# second pane, functional stuff:
tabs = ttk.Notebook(f2)
tabs.pack(fill=BOTH, expand=1)
glob = ttk.Frame(tabs); # global leaderboards
play = ttk.Frame(tabs); # score
helpt = ttk.Frame(tabs); # score
tabs.add(glob, text='Global')
tabs.add(play, text='Player')
tabs.add(helpt, text='Help')
# global tab
inf2=Label(glob, text="Include first ... players")
inf2.pack(fill=BOTH, expand=1)
en = Entry(glob, textvariable=num)
en.pack(fill=BOTH, expand=1)
inf=Label(glob, text="Hacker ID's separated\nby comma's")
inf.pack(fill=BOTH, expand=1)
e = Entry(glob, textvariable=hack)
e.pack(fill=BOTH, expand=1)
st=Label(glob, textvariable=status)
st.pack(fill=BOTH, expand=1)
status.set("Idle...")
startb = Button(glob, text='Start!', anchor="w", command=GlobalLeaderboards)
startb.pack(fill=BOTH, expand=1)    
#player tab
inf3=Label(play, text="Player ID")
inf3.pack(fill=BOTH, expand=1)
en3 = Entry(play, textvariable=num2)
en3.pack(fill=BOTH, expand=1)
st2 = Entry(play, textvariable=status2, state='readonly', readonlybackground='white', fg='black')
st2.pack()
st2.configure(relief=FLAT)
status2.set("Idle...")
startb2 = Button(play, text='Start!', anchor="w", command=lambda: GetPlayerScore(num2.get(), True))
startb2.pack(fill=BOTH, expand=1)     
#help tab
w = Label(helpt, wraplength=400, justify=LEFT)
w.pack(fill=BOTH, expand=1)
w.configure(text="**What is a Steam ID?\n The steam ID is the unique number assigned to each steam account"+ \
"that is used to identify accounts.\n\n"+\
"**How do I find a steam ID?\n -Go to your steam profile page in your browser."+\
"-Look at the URL. There are now 2 possibilities:\n"+\
"A It looks like http://steamcommunity.com/profiles/[somelongnumber]. You're in luck, [somelongnumber] is your steam ID.\n"+\
"B It looks different. The you have to go a step further:\n"+\
"-Add /?xml=1 to the url so it looks like http://steamcommunity.com/id/dinosawer/?xml=1 \n"+
"Somewhere at the top (2nd or 3rd line) there is a line that looks like <steamID64>[somenumber]</steamID64>\n"+\
"[somenumber] is your steamID.\n")


root.mainloop()
