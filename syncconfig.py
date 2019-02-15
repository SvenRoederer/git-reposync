
REPODIR="/tmp/gitsync"

REPOLIST = [
    {
#    "srcrepo" : "https://github.com/openwrt/openwrt.git",
#    "dstrepo" : "https://github.com/freifunk-berlin/openwrt-core.git",
    "srcremote" : "upstream",
    "dstremote" : "origin",
    "workdir" : "openwrt", 
    "user" : "SAm0815",
    "pass" : "test",
    "branches" : {
        "master" : "master",
        "lede-17.01" : "lede-17.01",
        },
    }, {
#    "srcrepo" : "https://github.com/openwrt/luci.git",
#    "dstrepo" : "https://github.com/freifunk-berlin/openwrt-luci.git",
    "srcremote" : "upstream",
    "dstremote" : "origin",
    "workdir" : "luci", 
    "user" : "SAm0815",
    "pass" : "test",
    "branches" : {
        "master" : "master",
        },
    },
]
