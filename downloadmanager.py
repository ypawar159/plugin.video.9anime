import xmlrpclib
from xbmcswift2 import xbmcgui
from resources.lib.ui.utils import fetch_sources
from resources.lib.ui.test_utils import MockedDialog

dg = xbmcgui.Dialog()


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
            plugin.log.error(files)


def download_anime(plugin, browser, anime, anime_name):
    pass
    plugin.log.info("Anime : " + anime)
    plugin.log.info("Anime Name : " + anime_name)
    # episodes = browser.get_anime_episodes(anime, True)
    # plugin.log.info(episodes[0])
    # episode_number = episodes[0]["url"].split("/")[-1]
    # sources = browser.get_episode_sources(anime, int(episode_number))
    # plugin.log.info(sources)
    dtype = dg.select("Select Download Type", ["All", "Selected", "Range"])
    plugin.log.info(dtype)
    if dtype != -1:
        res = browser._get_anime_info(anime)['RapidVideo']
        for r in res:
            r["name"] = " ".join([anime_name, " Episode ", str(r["id"])])
        # plugin.log.info(res)
        episodes = map(lambda x: "Episode " + str(x["id"]), res)
        # All
        if dtype == 0:
            fetch_downloads(plugin, res[0:2])
        if dtype == 1:
            selected = dg.multiselect("Select Episodes", episodes)
            plugin.log.info(selected)
            if selected:
                eps = []
                for i in selected:
                    # plugin.log.info(res[i])
                    eps.append(res[i])
                fetch_downloads(plugin, eps)
        if dtype == 2:
            start = dg.select("Select Start", episodes)
            if start != -1:
                end = dg.select("Select End", episodes)
                if end != -1:
                    if start > end:
                        eps = res[end:start + 1]
                    elif start < end:
                        eps = res[start:end + 1]
                    else:
                        eps = [res[start]]
                    plugin.log.info(start)
                    plugin.log.info(end)
                    plugin.log.info(eps)
                    fetch_downloads(plugin, eps)


def fetch_downloads(plugin, episode_list):
    downloads=[]
    for episode in episode_list:
        fetched = fetch_sources([('RapidVideo',episode["source"])],MockedDialog(),True)
        plugin.log.info(fetched)
        downloads.append((episode["name"],fetched.values()[0]))
    aria2_download(plugin,downloads)
