
REPODIR="/home/sven/git-sync/repos"

REPOLIST = {
    "repodir" : "ffb-firmware",
    "workbranch" : "daily_upstream",
    "srcremote" : "ff-berlin",
    }

UPDATES = {
  "openwrt": {
    "repodir" : "openwrt-core",
    "branch" : "master",
    "committext" : "Update to HEAD of OpenWrt-master",
    },
  "luci": {
    "repodir" : "openwrt-luci",
    "branch" : "master",
    "committext" : "Update LuCI-feed to yesterdays HEAD of master",
    },
  "packages": {
    "repodir" : "openwrt-packages",
    "branch" : "master",
    "committext" : "Updating packages to yesterdays HEAD of master",
    },
  "routing": {
    "repodir" : "openwrt-routing",
    "branch" : "master",
    "committext" : "Updating routing to yesterdays HEAD of master",
    },
  }

