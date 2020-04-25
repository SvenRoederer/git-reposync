#!/usr/bin/python

from git import Repo, Remote
import os, datetime, sys
import re,tempfile
import getopt
from importlib import import_module


def getFeeds():
  feeds = []
  with open(os.path.join(REPODIR, REPOLIST["repodir"], "feeds.conf")) as f:
    for line in f:
#      print(line)
      if line.startswith("#"):
        pass
      elif line == os.linesep:
        pass
      else:
        feedname = line.split(" ", 3)[1]
        print("found feed: %s" % feedname)
        feeds.append(feedname)
  f.closed
  return feeds

def isRepoAFeed(reponame):
  if reponame in FEEDS:
    return True
  else:
    return False


def getCurrentCommit(reponame):

  if reponame == "openwrt":
    filename = "config.mk"
    lineRegex = "^OPENWRT_COMMIT="
  elif isRepoAFeed(reponame):
    filename = "feeds.conf"
    lineRegex = "^src-git " + reponame + "*.\^"
    lineRegex = "^src-git " + reponame + " .*\^[a-f0-9]{40}"
#  print(filename)

  file = open(os.path.join(REPODIR, REPOLIST["repodir"], filename), "r")

  for line in file:
#    print line
    if re.search(lineRegex, line):
      print line,
      match = line.rstrip(os.linesep)
  file.close()

  result = re.split("=|\^", match)
  commit = result[1]
#  print(commit)

  return(commit)


def getYesterdaysLastCommit(reponame, date, branch = 'master'):

  if reponame == "openwrt":
    filename = "config.mk"
    lineRegex = "^OPENWRT_COMMIT="
  elif isRepoAFeed(reponame):
    filename = "feeds.conf"
    lineRegex = "^src-git " + reponame + "*.\^"
    lineRegex = "^src-git " + reponame + " .*\^[a-f0-9]{40}"
  else:
    print("faulty reponame")
    sys.quit(10)

  shellcmd = "(cd %s; git >/dev/null fetch --all; git rev-list -1 --before='%s' %s)" % (os.path.join(REPODIR, UPDATES[reponame]["repodir"]), date.strftime("%Y-%m-%d %H:%M"), branch)
  print(shellcmd)
  result = os.popen(shellcmd).readlines()

  result = result[0].rstrip(os.linesep)
  print(result)
  return result


def updateCommit(reponame, oldcommit, newcommit):

  if reponame == "openwrt":
    filename = "config.mk"
    lineRegex = "^OPENWRT_COMMIT="
  elif isRepoAFeed(reponame):
    filename = "feeds.conf"
    lineRegex = "^src-git " + reponame + "*.\^"
    lineRegex = "^src-git " + reponame + " .*\^[a-f0-9]{40}"

  shellcmd = "sed -i -e 's/%s/%s/' %s" % (oldcommit, newcommit, os.path.join(REPODIR, REPOLIST["repodir"], filename))
  print(shellcmd)
  os.popen(shellcmd).readlines()


def makeCommitMsg(reponame, message, oldcommit, newcommit):

  if reponame == "openwrt":
    filename = "config.mk"
    lineRegex = "^OPENWRT_COMMIT="
  elif isRepoAFeed(reponame):
    filename = "feeds.conf"
    lineRegex = "^src-git " + reponame + "*.\^"
    lineRegex = "^src-git " + reponame + " .*\^[a-f0-9]{40}"

  shellcmd = "(cd %s; git log --oneline --reverse '%s..%s')" % (os.path.join(REPODIR, UPDATES[reponame]["repodir"]), oldcommit, newcommit)
  print(shellcmd)
  msgbody = os.popen(shellcmd).read()

  msgFile = tempfile.NamedTemporaryFile()
  msgFile.write(message + os.linesep)
  msgFile.write(os.linesep)
  msgFile.write(msgbody)
  msgFile.flush()
  shellcmd = "(cd %s; git commit --no-edit -F '%s' '%s')" % (os.path.join(REPODIR, REPOLIST["repodir"]), msgFile.name, filename)
  print(shellcmd)
  result = os.popen(shellcmd).readlines()
  print(result)
#  result = os.popen("echo check tempfile; sleep 20").readlines() 
  msgFile.close()

  return 


##############################################################

COMMITS_INITIAL = {}
COMMITS_FINAL   = {}

configfile = "ff-berlin_update"
try:
    opts, args = getopt.getopt(sys.argv[1:],"hf:",["conf="])
except getopt.GetoptError:
    print 'test.py -f <configfile>'
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print 'test.py -f <configfile>'
        sys.exit()
    elif opt in ("-f", "--ifile"):
        configfile = arg
print('Config file is', configfile)

config = import_module(configfile)

REPODIR = config.REPODIR
REPOLIST = config.REPOLIST
UPDATES = config.UPDATES

TODAY = datetime.datetime.now()
DATELIMIT = TODAY-datetime.timedelta(days=0)
print(DATELIMIT)

FEEDS = getFeeds()
shellcmd = "(cd %s; git checkout '%s')" % (os.path.join(REPODIR, REPOLIST["repodir"]), REPOLIST["workbranch"])
print(shellcmd)
result = os.popen(shellcmd).readlines()
shellcmd = "(cd %s; git fetch )" % (os.path.join(REPODIR, REPOLIST["repodir"]))
print(shellcmd)
result = os.popen(shellcmd).readlines()
shellcmd = "(cd %s; git reset --hard %s/%s )" % (os.path.join(REPODIR, REPOLIST["repodir"]), REPOLIST["srcremote"], REPOLIST["workbranch"])
print(shellcmd)
result = os.popen(shellcmd).readlines()


COMMITS_INITIAL["openwrt"] = getCurrentCommit("openwrt")
for feed in FEEDS:
  if feed in UPDATES.keys():
    COMMITS_INITIAL[feed] = getCurrentCommit(feed)
print("initial: %s" % (COMMITS_INITIAL))

COMMITS_FINAL["openwrt"] = getYesterdaysLastCommit("openwrt", DATELIMIT, UPDATES["openwrt"]["branch"])
for feed in FEEDS:
  if feed in UPDATES.keys():
    COMMITS_FINAL[feed] = getYesterdaysLastCommit(feed, DATELIMIT, UPDATES[feed]["branch"])
print("target: %s" % (COMMITS_FINAL))

updateCommit("openwrt", COMMITS_INITIAL["openwrt"], COMMITS_FINAL["openwrt"])
makeCommitMsg("openwrt", UPDATES["openwrt"]["committext"], COMMITS_INITIAL["openwrt"], COMMITS_FINAL["openwrt"])
for feed in FEEDS:
  if feed in UPDATES.keys():
    updateCommit(feed, COMMITS_INITIAL[feed], COMMITS_FINAL[feed])
    makeCommitMsg(feed, UPDATES[feed]["committext"], COMMITS_INITIAL[feed], COMMITS_FINAL[feed])

if REPOLIST["autopush"]:
  print "pushing changes to repo"
  shellcmd = "(cd %s; git push %s)" % (os.path.join(REPODIR,REPOLIST["repodir"]), REPOLIST["srcremote"])
  print(shellcmd)
  result = os.popen(shellcmd).readlines()
