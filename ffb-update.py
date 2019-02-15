#!/usr/bin/python

from git import Repo, Remote
import os, datetime, sys
import re,tempfile
import getopt
from importlib import import_module


def isRepoAFeed(reponame):
  FEEDS = {
    "packages",
    "luci",
    "routing", 
    "packages_berlin",
    "gluon",
  }

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

  shellcmd = "(cd %s; git >/dev/null fetch --all; git rev-list -1 --before='%s' %s)" % (os.path.join(REPODIR, UPDATES[reponame]["repodir"]), date.strftime("%Y-%m-%d"), branch)
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
COMMITS_INITIAL["packages"] = getCurrentCommit("packages")
COMMITS_INITIAL["luci"] = getCurrentCommit("luci")
COMMITS_INITIAL["routing"] = getCurrentCommit("routing")
COMMITS_INITIAL["packages_berlin"] = getCurrentCommit("packages_berlin")
COMMITS_INITIAL["gluon"] = getCurrentCommit("gluon")
print("initial: %s" % (COMMITS_INITIAL))

COMMITS_FINAL["openwrt"] = getYesterdaysLastCommit("openwrt", DATELIMIT, UPDATES["openwrt"]["branch"])
COMMITS_FINAL["packages"] = getYesterdaysLastCommit("packages", DATELIMIT, UPDATES["packages"]["branch"])
COMMITS_FINAL["luci"] = getYesterdaysLastCommit("luci", DATELIMIT, UPDATES["luci"]["branch"])
COMMITS_FINAL["routing"] = getYesterdaysLastCommit("routing", DATELIMIT, UPDATES["routing"]["branch"])
COMMITS_FINAL["packages_berlin"] = getYesterdaysLastCommit("packages_berlin", DATELIMIT, UPDATES["packages_berlin"]["branch"])
COMMITS_FINAL["gluon"] = getYesterdaysLastCommit("gluon", DATELIMIT, UPDATES["gluon"]["branch"])
print("target: %s" % (COMMITS_FINAL))

updateCommit("openwrt", COMMITS_INITIAL["openwrt"], COMMITS_FINAL["openwrt"])
makeCommitMsg("openwrt", UPDATES["openwrt"]["committext"], COMMITS_INITIAL["openwrt"], COMMITS_FINAL["openwrt"])
updateCommit("packages", COMMITS_INITIAL["packages"], COMMITS_FINAL["packages"])
makeCommitMsg("packages", UPDATES["packages"]["committext"], COMMITS_INITIAL["packages"], COMMITS_FINAL["packages"])
updateCommit("luci", COMMITS_INITIAL["luci"], COMMITS_FINAL["luci"])
makeCommitMsg("luci", UPDATES["luci"]["committext"], COMMITS_INITIAL["luci"], COMMITS_FINAL["luci"])
updateCommit("routing", COMMITS_INITIAL["routing"], COMMITS_FINAL["routing"])
makeCommitMsg("routing", UPDATES["routing"]["committext"], COMMITS_INITIAL["routing"], COMMITS_FINAL["routing"])
updateCommit("packages_berlin", COMMITS_INITIAL["packages_berlin"], COMMITS_FINAL["packages_berlin"])
makeCommitMsg("packages_berlin", UPDATES["packages_berlin"]["committext"], COMMITS_INITIAL["packages_berlin"], COMMITS_FINAL["packages_berlin"])
updateCommit("gluon", COMMITS_INITIAL["gluon"], COMMITS_FINAL["gluon"])
makeCommitMsg("gluon", UPDATES["gluon"]["committext"], COMMITS_INITIAL["gluon"], COMMITS_FINAL["gluon"])
