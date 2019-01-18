#!/usr/bin/python3

# https://gitpython.readthedocs.io/en/stable/tutorial.html#tutorial-label

from git import Repo, Remote
import os

import syncconfig

REPODIR = syncconfig.REPODIR
REPOLIST = syncconfig.REPOLIST

def syncrepo(workdir, user, passw, src, dst, srcbranch, dstbranch):
    #https://stackoverflow.com/questions/44784828/gitpython-git-authentication-using-user-and-password?noredirect=1&lq=1
    project_dir = os.path.dirname(os.path.abspath(__file__))
    os.environ['GIT_ASKPASS'] = os.path.join(project_dir, 'askpass.py')

    repo = Repo(os.path.join(REPODIR, workdir))
    assert not repo.bare
    print (repo.remotes)
    remotefrom=repo.remote(name=src)
    remoteto=repo.remote(name=dst)
    fetchinfo=remotefrom.fetch()
#    print(fetchinfo.ref)
    if dstbranch in repo.heads:
        print("branch '%s' exists" % dstbranch)
    else:
        print("branch '%s' needs to be created" % dstbranch)
        repo.create_head(dstbranch, src+"/"+srcbranch)
#    workbranch = repo.heads[srcbranch].checkout(force=True)
#    print(workbranch)
#    workbranch.set_commit(srcbranch).commit
#    repo.head.reference=srcbranch
    repo.git.checkout(dstbranch)
    repo.head.reset(src+"/"+srcbranch, index=True, working_tree=True)
#    workbranch.reset()
#    repo.heads[srcbranch].HEAD.reset()
#    print(repo.heads["sync"])
    remotefrom.pull(refspec=srcbranch)
    remoteto.push(refspec=dstbranch)

############## main ###################

for repodata in REPOLIST:
    print(repodata)
#    print(repodata["srcrepo"])
#    print(repodata["dstrepo"])
    print(repodata["user"])
    print(repodata["pass"])
    print(repodata["branches"])
    syncbranches=repodata["branches"]
    for srcbranch, dstbranch in syncbranches.items():
        print('sync %s to %s' % (srcbranch, dstbranch))
#        print('sync %s/%s to %s/%s as user %s' % (repodata["srcrepo"], srcbranch, repodata["dstrepo"], dstbranch, repodata["user"]) )
        syncrepo( repodata["workdir"], repodata["user"], repodata["pass"], repodata["srcremote"], repodata["dstremote"], srcbranch, dstbranch)
