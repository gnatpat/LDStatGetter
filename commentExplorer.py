import urllib.request
from time import sleep
from GUI import Application
from GUI.Alerts import alert

import threading
from queue import Queue

printLock = threading.Lock()
highestLock = threading.Lock()
usersLock = threading.Lock()
users = {}
highest = 0;

class Entry(object):
    def __init__(self, gameId):
        self.gameId = gameId;
        self.gameName = "";
        self.comments = [];
        self.commentsWritten = 0;
        self.commentedOn = []
        self.getting = False;

class EntryInfo(object):
    def __init__(self, gameName, gameId, comments):
        self.gameId = gameId
        self.comments = comments
        self.gameName = gameName

def extract(html):
    html = html.replace("<br/>", "\n");
    user = html.split("<a")[1].split(">")[1].split("<")[0]
    userId = html.split("<a href=")[1].split('">')[0].split("uid=")[1]
    comment = html.split("<p>")[1].split("</p>")[0]
    return user, userId, comment

def getExtracted(gameId):
    page = urllib.request.urlopen("http://ludumdare.com/compo/ludum-dare-20/?action=preview&uid=" + gameId).read()
    text = page.decode("utf-8")
    comments = (text.split("<div class = 'comment'>"))
    if (len(comments) == 1):
        return None;

    comments.pop(0);
    comments[-1] = comments[-1].split("<p>You must sign in to comment.</p>")[0]
    gameName = text.split("<h2 style='font-size:28px'>")[1].split("</h2>")[0];
    return EntryInfo(gameName, gameId, list(map(extract, comments)))

def fetchWorker():
    while(True):
        gameId = idQueue.get()
    
        entryInfo = getExtracted(gameId)
        if (entryInfo != None):
            entryQueue.put(entryInfo);
        idQueue.task_done()

def exploreGame(entryInfo):
    global highest

    gameId = entryInfo.gameId;
    comments = entryInfo.comments;
    name = entryInfo.gameName;

    with usersLock:
        users[gameId].comments = comments
        users[gameId].gameName = entryInfo.gameName

    with highestLock:
        if(highest <= len(comments)):
            highest = len(comments)
            with printLock:
                print("---------- " + name + " (" + str(gameId) + ") has the most comments with " + str(highest) + " ----------")

    with printLock:
        print("Added '" + name + "' (" + str(gameId) + ") with " + str(len(comments)) + " comments.")


    for user, userId, comment in comments:
        with usersLock:
            if(userId not in users):
                idQueue.put(userId)
                users[userId] = Entry(gameId)
            if(gameId not in users[userId].commentedOn):
                users[userId].commentsWritten += 1
                users[userId].commentedOn.append(gameId)

def exploreWorker():
    while True:
        entryInfo = entryQueue.get()

        exploreGame(entryInfo)
        entryQueue.task_done()

entryQueue = Queue();
idQueue = Queue();

for i in range(8):
    t = threading.Thread(target=fetchWorker)
    t.start()

for i in range(8):
    t = threading.Thread(target=exploreWorker)
    t.start()

gameId = input("Enter a game id to start with: ")
users[gameId] = Entry(gameId);
idQueue.put(gameId)

entryQueue.join();
idQueue.join();
entryQueue.join();
idQueue.join();
entryQueue.join();
idQueue.join();
entryQueue.join();
idQueue.join();
entryQueue.join();
idQueue.join();
entryQueue.join();
idQueue.join();
entryQueue.join();
idQueue.join();
entryQueue.join();
idQueue.join();

def getCommentsWritten(x):
    (_, user) = x
    return user.commentsWritten;
def getCommentsGot(x):
    (_, user) = x
    return len(user.comments);

byCommentsWritten = sorted(list(users.items()), key = getCommentsWritten, reverse=True);
byCommentsGot = sorted(list(users.items()), key = getCommentsGot, reverse=True);

print("Top 100 commented games: ");
for i in range(10):
    gameId, user = byCommentsGot[i];
    print(user.gameName + " (" + str(user.gameId) + "): " + str(len(user.comments)))


print("Top 100 users that comment: ");
for i in range(10):
    gameId, user = byCommentsWritten[i];
    print(user.gameName + " (" + str(user.gameId) + "): " + str(user.commentsWritten))
