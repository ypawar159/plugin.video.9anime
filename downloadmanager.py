import xmlrpclib
from xbmcswift2 import xbmcgui
from resources.lib.ui.utils import fetch_sources
import re

parse_resolution = re.compile(r"\d+")
dg = xbmcgui.Dialog()
resolutions = [1080, 720, 480, 360]


class MockedDialog(object):
    def __init__(self):
        pass

    def update(self, precentage, name=None):
        pass

    def iscanceled(self):
        return False


def select_resolution(resolutions, available, preferred):
    if len(available) == 0:
        return

    elif len(available) == 1:
        return available[0]

    elif preferred in available:
        return preferred
    else:
        index = resolutions.index(preferred) + 1
        # try lower resolutions first
        # decided = False
        while index < len(resolutions):
            if resolutions[index] in available:
                return resolutions[index]
            index += 1
        # try higher resolutions
        index = resolutions.index(preferred) - 1
        while index > -1:
            if resolutions[index] in available:
                return resolutions[index]
            index -= 1
    # If available not in resolutions return None though error would have been better
    return


# plugin : xbmcswift2.Plugin object
# files : list of tuples/list for (filename,url)
def aria2_download(plugin, files):
    aria_url = "http://{}:{}/rpc".format(plugin.get_setting('ipaddress'), plugin.get_setting('port'))
    aria_server = xmlrpclib.ServerProxy(aria_url, verbose=False)
    paused = plugin.get_setting("paused")
    tkn = 'token:{}'.format(plugin.get_setting('rpcsecret'))
    if len(files) > 0:
        for f in files:
            try:
                gid = aria_server.aria2.addUri(tkn, [f[1]], {'pause': paused, 'out': f[0]})
                if gid:
                    plugin.notify("Download Added")
            except Exception as e:
                plugin.notify("Download Failed")
                plugin.log.error(e)
                plugin.log.error(files)
    else:
        plugin.notify("Nothing to Download")
        plugin.log.error("Nothing to Download")


def download_anime(plugin, browser, anime, anime_name):
    plugin.log.info("Anime : " + anime)
    plugin.log.info("Anime Name : " + anime_name)
    # episodes = browser.get_anime_episodes(anime, True)
    # plugin.log.info(episodes[0])
    # episode_number = episodes[0]["url"].split("/")[-1]
    sources = browser.get_episode_sources(anime, 1)
    plugin.log.info(len(sources))
    plugin.log.info(sources)
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
    preferred_resolution = int(plugin.get_setting("prefres")[:-1])
    downloads = []
    for episode in episode_list:
        fetched = fetch_sources([('RapidVideo', episode["source"])], MockedDialog(), True)
        plugin.log.info(fetched)
        if fetched:
            available_resolutions = {}
            for k, v in fetched.items():
                available_resolutions[int(parse_resolution.findall(k[5:])[0])] = v
            plugin.log.info("Available Resolutions: " + str(sorted(available_resolutions)))
            selected_resolution = select_resolution(resolutions, available_resolutions.keys(), preferred_resolution)
            filename = "{} ({}p).mp4".format(episode["name"], selected_resolution)
            plugin.log.info("Adding : " + filename)
            downloads.append((filename, available_resolutions[selected_resolution]))
    aria2_download(plugin, downloads)
