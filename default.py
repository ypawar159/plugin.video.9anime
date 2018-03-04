from resources.lib.ui import utils
from resources.lib.ui.SourcesList import SourcesList
from resources.lib.NineAnimeBrowser import NineAnimeBrowser
from xbmcswift2 import Plugin, actions
from urllib import urlencode
import downloadmanager as dm

# from kodiswift import Plugin

try:
    import xbmc

    running_cli = False
except ImportError:
    running_cli = True

plugin = Plugin()
SERVER_CHOICES = {
    "serverg4": "Server G4",
    "serverrapid": "RapidVideo",
    "servermycloud": "MyCloud",
    "serveropenload": "OpenLoad",
}

_BROWSER = NineAnimeBrowser()


# Todo: Prevent crash if no data returned from browser functions
def url_for(url):
    # if url.startswith(starting):
    #     # return "plugin://{}/{}/{}".format(plugin.id, url, quote(data))
    #     return "plugin://{}/{}?{}".format(plugin.id, url, urlencode(data))
    # else:
    return "plugin://{}/{}".format(plugin.id, url)
    # plugin.url_for(url.split("/")[0],)


def create_url(url, data=None, download=False):
    url_parts = url.split("/")
    if url.startswith("animes"):
        return plugin.url_for("animes", anime=url_parts[-1], anime_name=data.encode("utf-8"), download=download)
    if url.startswith("play"):
        return plugin.url_for("play", anime=url_parts[-2], episode_number=url_parts[-1],
                              anime_name=data)
    else:
        return url_for(url)


def isDirectoryStyle():
    style = plugin.get_setting('displaystyle')
    return "Directory" == style


def sortResultsByRes(fetched_urls):
    prefereResSetting = utils.parse_resolution_of_source(plugin.get_setting('prefres'))
    filtered_urls = filter(lambda x: utils.parse_resolution_of_source(x[0]) <= prefereResSetting, fetched_urls)
    return sorted(filtered_urls, key=lambda x: utils.parse_resolution_of_source(x[0]), reverse=True)


MENU_ITEMS = [
    ("Latest", "latest_d"),
    ("Newest", "newest_d"),
    ("Recent Subbed", "recent_subbed_d"),
    ("Popular Subbed", "popular_subbed_d"),
    ("Recent Dubbed", "recent_dubbed_d"),
    ("Popular Dubbed", "popular_dubbed_d"),
    ("Genres", "genres"),
    ("Search", "search_d"),
    ("Settings", "settings")
]


@plugin.route("/latest", name="latest_d", options={"page": "1"})
@plugin.route("/latest/<page>")
def latest(page):
    plugin.log.info(page)
    animes = _BROWSER.get_latest(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        items.append(
            {
                "label": anime["name"],
                "path": create_url(anime["url"], anime["name"]),
                "context_menu": [("Download", actions.background(
                    create_url(anime["url"], anime["name"], True)))]
            }
        )
    return plugin.finish(items)


@plugin.route("/animes/<anime>")
def animes(anime):
    plugin.log.info(anime)
    anime_name = plugin.request.args["anime_name"][0]
    download = "True" == plugin.request.args["download"][0]
    if download:
        dm.download_anime(plugin,anime,anime_name)
    # plugin.log.info(anime_name)
    # print(anime_name)
    plugin.log.info(anime_name)
    episodes = _BROWSER.get_anime_episodes(anime, isDirectoryStyle())
    plugin.log.info(episodes[0])
    plugin.log.info(episodes[-1])
    items = []
    for episode in episodes:
        items.append(
            {
                "label": episode["name"],
                "path": create_url(episode["url"], anime_name)
            }
        )
    return plugin.finish(items)


@plugin.route("/play/<anime>/<episode_number>")
def play(anime, episode_number):
    anime_name = plugin.request.args["anime_name"][0]
    plugin.log.info("Name: " + anime_name)
    plugin.log.info("Anime: {} Episode: {}".format(anime, episode_number))
    sources = _BROWSER.get_episode_sources(anime, int(episode_number))
    serverChoice = filter(lambda x: plugin.get_setting(x[0]) == 'true', SERVER_CHOICES.iteritems())
    serverChoice = map(lambda x: x[1], serverChoice)
    sources = filter(lambda x: x[0] in serverChoice, sources)
    autoplay = True if 'true' in plugin.get_setting('autoplay') else False
    s = SourcesList(sources, autoplay, sortResultsByRes, {
        'title': "Fetching Sources",
        'processing': "Processing %s",
        'choose': "Please choose source: ",
        'notfound': "Couldn't find eligible sources",
    })
    if running_cli:
        return plugin.finish([])
    else:
        if isDirectoryStyle():
            if s._read_sources():
                items = sorted(s._sources.iteritems(), key=lambda x: x[0])
                items = [(title[5:], url) for title, url in items]
                plugin.log.info(items)
                plugin.log.info(items[0])
                items = map(
                    lambda x: {"label": x[0], "is_playable": True,
                               "path": plugin.url_for("playlink", url=x[1], anime_name=anime_name,
                                                      episode_number=episode_number, download=False),
                               "context_menu": [("Download", actions.background(
                                   plugin.url_for("playlink", url=x[1], anime_name=anime_name,
                                                  episode_number=episode_number, download=True)))]}, items)
                plugin.log.info(items)
                return plugin.finish(items)
        else:
            link = s.get_video_link()
            plugin.log.info("Playlink: " + link)
            item = {"label": anime, "path": link}
            return plugin.play_video(item)


@plugin.route("/playlink/<url>")
def playlink(url):
    anime_name = plugin.request.args["anime_name"][0]
    episode_number = plugin.request.args["episode_number"][0]
    download = "True" == plugin.request.args["download"][0]
    fname = anime_name + " Episode " + episode_number
    if download:
        return dm.aria2_download(plugin, [(fname, url)])
    item = {"label": fname, "path": url}
    return plugin.play_video(item)


@plugin.route("/newest", name="newest_d", options={"page": "1"})
@plugin.route("/newest/<page>")
def newest(page):
    plugin.log.info(page)
    animes = _BROWSER.get_newest(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        items.append(
            {
                "label": anime["name"],
                "path": create_url(anime["url"], anime["name"])
            }
        )
    return plugin.finish(items)


@plugin.route("/recent_subbed", name="recent_subbed_d", options={"page": "1"})
@plugin.route("/recent_subbed/<page>")
def recent_subbed(page):
    plugin.log.info(page)
    animes = _BROWSER.get_recent_subbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        items.append(
            {
                "label": anime["name"],
                "path": create_url(anime["url"], anime["name"])
            }
        )
    return plugin.finish(items)


@plugin.route("/popular_subbed", name="popular_subbed_d", options={"page": "1"})
@plugin.route("/popular_subbed/<page>")
def popular_subbed(page):
    plugin.log.info(page)
    animes = _BROWSER.get_popular_subbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        items.append(
            {
                "label": anime["name"],
                "path": create_url(anime["url"], anime["name"])
            }
        )
    return plugin.finish(items)


@plugin.route("/recent_dubbed", name="recent_dubbed_d", options={"page": "1"})
@plugin.route("/recent_dubbed/<page>")
def recent_dubbed(page):
    plugin.log.info(page)
    animes = _BROWSER.get_recent_dubbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        items.append(
            {
                "label": anime["name"],
                "path": create_url(anime["url"], anime["name"])
            }
        )
    return plugin.finish(items)


@plugin.route("/popular_dubbed", name="popular_dubbed_d", options={"page": "1"})
@plugin.route("/popular_dubbed/<page>")
def popular_dubbed(page):
    plugin.log.info(page)
    animes = _BROWSER.get_popular_dubbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        items.append(
            {
                "label": anime["name"],
                "path": create_url(anime["url"], anime["name"])
            }
        )
    return plugin.finish(items)


@plugin.route("/genres")
def genres():
    genres = _BROWSER.get_genres()
    plugin.log.info(genres[0])
    items = []
    for genre in genres:
        items.append(
            {
                "label": genre["name"],
                "path": url_for(genre["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/genre/<name>/<page>")
def genre(name, page):
    animes = _BROWSER.get_genre(name, int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        items.append(
            {
                "label": anime["name"],
                "path": create_url(anime["url"], anime["name"])
            }
        )
    return plugin.finish(items)


@plugin.route("/search", name="search_d", options={"query": "", "page": "1"})
@plugin.route("/search/<query>/<page>")
def search(query, page):
    if query == "":
        query = plugin.keyboard(heading="Search Anime")
    plugin.log.info(page)
    if query:
        animes = _BROWSER.search_site(query, int(page))
        plugin.log.info(animes[0])
        plugin.log.info(animes[-1])
        items = []
        for anime in animes:
            items.append(
                {
                    "label": anime["name"],
                    "path": create_url(anime["url"], anime["name"])
                }
            )
        return plugin.finish(items)


@plugin.route("/settings")
def settings():
    if running_cli:
        return plugin.finish([])
    return plugin.open_settings()


@plugin.route('/')
def list_menu():
    items = []
    for name, url in MENU_ITEMS:
        items.append({"label": name, "path": plugin.url_for(url)})
    return items


if __name__ == '__main__':
    plugin.run()
    plugin.set_content("tvshows")
