import xmlrpclib

# plugin : xbmcswift2.Plugin object
# files : list of tuples/list for (filename,url)
def aria2_download(plugin, files):
    aria_url = "http://{}:{}/rpc".format(plugin.get_setting('ipaddress'), plugin.get_setting('port'))
    aria_server = xmlrpclib.ServerProxy(aria_url, verbose=False)
    paused = plugin.get_setting("paused")
    tkn = 'token:{}'.format(plugin.get_setting('rpcsecret'))
    for f in files:
        try:
            gid = aria_server.aria2.addUri(tkn, [f[1]], {'pause': paused, 'out': f[0]})
            if gid:
                plugin.notify("Download Added")
        except Exception as e:
            plugin.notify("Download Failed")
            plugin.log.error(e)
