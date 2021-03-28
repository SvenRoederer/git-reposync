#!/usr/bin/python3

from git import Repo, Remote
import os, datetime, sys
import re,tempfile
import getopt
from importlib import import_module

def utc_to_local(utc_dt):
    return utc_dt.replace(tzinfo=datetime.timezone.utc).astimezone(tz=None)

def getRepoNames():
  repos = []
  with open(os.path.join(REPODIR, REPOLIST["repodir"], "modules")) as f:
    for line in f:
#      print(line)
      if line.startswith("#"):
        pass
      elif line == os.linesep:
        pass
      elif line.startswith("PACKAGES_"):
        pass
      elif line.startswith("OPENWRT_REPO="):
        repos.append("openwrt")
#      elif re.match("^OPENWRT_COMMIT=[a-f0-9]{40}", line):
      elif re.match("^OPENWRT_(COMMIT|BRANCH)=[a-zA-Z0-9_\-\.]+$", line):
        print("Found %s" % line.strip())
        pass
      elif line.startswith("GLUON_FEEDS="):
        bad_chars = ['\'', '\"'] 
        packages=line.split("=")[1]
#        print(packages)
        packages = ''.join( filter(lambda i: i not in bad_chars, packages) )
#        print(packages)
        for repo in packages.split():
          repos.append(repo)
      else:
        print("unknown line found in modules-file")
        print("  %s" % line)
        sys.exit(1)
  f.closed
  return repos


def getCurrentCommit(reponame):

  if reponame == "openwrt":
    lineRegex = "^OPENWRT_COMMIT="
  else:
    lineRegex = "^PACKAGES_" + reponame.upper() + " .*\^[a-f0-9]{40}"
    lineRegex = "^PACKAGES_" + reponame.upper() + "_COMMIT=[a-f0-9]{40}"

  file = open(os.path.join(REPODIR, REPOLIST["repodir"], 'modules'), "r")

  for line in file:
#    print line
    if re.search(lineRegex, line):
      print (line)
      match = line.rstrip(os.linesep)
  file.close()

  result = re.split("=|\^", match)
  commit = result[1]
#  print(commit)

  return(commit)


def getYesterdaysLastCommit(reponame, date, branch = 'master'):

  if reponame == "openwrt":
    lineRegex = "^OPENWRT_COMMIT="
  else:
    lineRegex = "^PACKAGES_" + reponame.upper() + " .*\^[a-f0-9]{40}"
    lineRegex = "^PACKAGES_" + reponame.upper() + "_COMMIT=[a-f0-9]{40}"

  shellcmd = "(cd %s; git >/dev/null fetch --all; git rev-list -1 --before='%s' %s)" % (os.path.join(REPODIR, UPDATES[reponame]["repodir"]), date.strftime("%Y-%m-%d %H:%M:%S"), branch)
  print(shellcmd)
  result = os.popen(shellcmd).readlines()

  result = result[0].rstrip(os.linesep)
  print(result)
  return result


def updateCommit(reponame, oldcommit, newcommit):

  if reponame == "openwrt":
    lineRegex = "^OPENWRT_COMMIT="
  else:
    lineRegex = "^PACKAGES_" + reponame.upper() + "_COMMIT=[a-f0-9]{40}"

  shellcmd = "sed -i -e 's/%s/%s/' %s" % (oldcommit, newcommit, os.path.join(REPODIR, REPOLIST["repodir"], 'modules'))
  print(shellcmd)
  os.popen(shellcmd).readlines()


def makeCommitMsg(reponame, message, oldcommit, newcommit):

  if reponame == "openwrt":
    lineRegex = "^OPENWRT_COMMIT="
  else:
    lineRegex = "^PACKAGES_" + reponame.upper() + "_COMMIT=[a-f0-9]{40}"

  shellcmd = "(cd %s; git log --oneline --reverse '%s..%s')" % (os.path.join(REPODIR, UPDATES[reponame]["repodir"]), oldcommit, newcommit)
  print(shellcmd)
  msgbody = os.popen(shellcmd).read()

  msgFile = tempfile.NamedTemporaryFile(mode='w')
  msgFile.write(message + os.linesep)
  msgFile.write(os.linesep)
  msgFile.write(msgbody)
  msgFile.flush()
  shellcmd = "(cd %s; git commit --no-edit -F '%s' '%s')" % (os.path.join(REPODIR, REPOLIST["repodir"]), msgFile.name, 'modules')
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
#TODAY = datetime.datetime.now()
TODAY = datetime.datetime.now().date()
#TODAY=datetime.datetime.min.time()
DATELIMIT=datetime.date(TODAY.year, TODAY.month, TODAY.day)
#DATELIMIT = DATELIMIT - datetime.timedelta(seconds=1)
DATELIMIT = datetime.datetime.combine(TODAY-datetime.timedelta(days=1), datetime.time.max)
#DATELIMIT = TODAY.date() + datetime.timedelta(hours=23)
#datetime.timedelta(days=0, hours=23, minutes=59, seconds=59)
#DATELIMIT = TODAY+datetime.timedelta(days=-3)
#DATELIMIT = datetime.date(2020, 03, 01,)

try:
    opts, args = getopt.getopt(sys.argv[1:],"hf:t:",["conf="])
except getopt.GetoptError:
    print ('test.py -f <configfile>')
    sys.exit(2)
for opt, arg in opts:
    if opt == '-h':
        print ('test.py -f <configfile>')
        sys.exit()
    elif opt in ("-f", "--ifile"):
        configfile = arg
    elif opt in ("-t", "--todate"):
        try:
           DATELIMIT = datetime.datetime.strptime(arg, "%Y-%m-%d")
        except ValueError:
           print("Unable to decode date. is format YYYY-MM-DD?")
           sys.exit()
print('Config file is', configfile)

config = import_module(configfile)

REPODIR = config.REPODIR
REPOLIST = config.REPOLIST
UPDATES = config.UPDATES

if not "dstremote" in REPOLIST:
    REPOLIST["dstremote"] = REPOLIST["srcremote"]

print(DATELIMIT)
DATELIMIT=utc_to_local(DATELIMIT)
print(DATELIMIT)

#sys.exit(1)

shellcmd = "(cd %s; git checkout '%s')" % (os.path.join(REPODIR, REPOLIST["repodir"]), REPOLIST["workbranch"])
print(shellcmd)
result = os.popen(shellcmd).readlines()
shellcmd = "(cd %s; git fetch %s)" % (os.path.join(REPODIR, REPOLIST["repodir"]), REPOLIST["srcremote"])
print(shellcmd)
result = os.popen(shellcmd).readlines()
shellcmd = "(cd %s; git reset --hard %s/%s )" % (os.path.join(REPODIR, REPOLIST["repodir"]), REPOLIST["srcremote"], REPOLIST["workbranch"])
print(shellcmd)
result = os.popen(shellcmd).readlines()


MODULES = getRepoNames()
ignoreModules = []
for module in MODULES:
  print("testing module %s" % module)
  if not module in UPDATES.keys():
    print("remove repo %s, which is not defined in config-file." % module)
    ignoreModules.append(module)

# removing the an individual module via MODULES.remove() will shorten the list by one element
# and the last element will not be tested. So using 2 lists and substracting them
# https://www.geeksforgeeks.org/python-difference-two-lists/
MODULES=(list(set(MODULES) - set(ignoreModules)))
MODULES.reverse()

for module in MODULES:
  COMMITS_INITIAL[module] = getCurrentCommit(module)
print("initial: %s" % (COMMITS_INITIAL))

for module in MODULES:
  COMMITS_FINAL[module] = getYesterdaysLastCommit(module, DATELIMIT, UPDATES[module]["branch"])
print("target: %s" % (COMMITS_FINAL))

for module in MODULES:
  updateCommit(module, COMMITS_INITIAL[module], COMMITS_FINAL[module])
  makeCommitMsg(module, UPDATES[module]["committext"], COMMITS_INITIAL[module], COMMITS_FINAL[module])

if "autopush" in REPOLIST and REPOLIST["autopush"]:
  print ("pushing changes to repo")
  shellcmd = "(cd %s; git push %s)" % (os.path.join(REPODIR,REPOLIST["repodir"]), REPOLIST["dstremote"])
  print(shellcmd)
  result = os.popen(shellcmd).readlines()
