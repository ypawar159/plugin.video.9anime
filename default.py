# from resources.lib.ui import control
from resources.lib.ui import utils
from resources.lib.ui.SourcesList import SourcesList
# from resources.lib.ui.router import route, router_process
from resources.lib.NineAnimeBrowser import NineAnimeBrowser
# import urlparse

from xbmcswift2 import Plugin

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


# Todo: Prevent crash if no data retruned from browser functions
def url_for(url):
    return "plugin://{}/{}".format(plugin.id, url)


def isDirectoryStyle():
    style = plugin.get_setting('displaystyle')
    return "Directory" == style


def sortResultsByRes(fetched_urls):
    prefereResSetting = utils.parse_resolution_of_source(plugin.get_setting('prefres'))

    filtered_urls = filter(lambda x: utils.parse_resolution_of_source(x[0]) <=
                                     prefereResSetting, fetched_urls)

    return sorted(filtered_urls, key=lambda x:
    utils.parse_resolution_of_source(x[0]),
                  reverse=True)


'''
AB_LIST = [".", "0"] + [chr(i) for i in range(ord("A"), ord("Z") + 1)]
MENU_ITEMS = [
    (control.lang(30000), "latest"),
    (control.lang(30001), "newest"),
    (control.lang(30002), "recent_subbed"),
    (control.lang(30003), "popular_subbed"),
    (control.lang(30004), "recent_dubbed"),
    (control.lang(30005), "popular_dubbed"),
    (control.lang(30006), "genres"),
    (control.lang(30007), "search"),
    (control.lang(30008), "settings")
]
SERVER_CHOICES = {
    "serverg4": "Server G4",
    "serverrapid": "RapidVideo",
    "servermycloud": "MyCloud",
    "serveropenload": "OpenLoad",
}

_BROWSER = NineAnimeBrowser()
control.setContent('tvshows');


def isDirectoryStyle():
    style = control.getSetting('displaystyle')
    return "Directory" == style


def sortResultsByRes(fetched_urls):
    prefereResSetting = utils.parse_resolution_of_source(control.getSetting('prefres'))

    filtered_urls = filter(lambda x: utils.parse_resolution_of_source(x[0]) <=
                                     prefereResSetting, fetched_urls)

    return sorted(filtered_urls, key=lambda x:
    utils.parse_resolution_of_source(x[0]),
                  reverse=True)


@route('settings')
def SETTINGS(payload):
    return control.settingsMenu();


@route('animes/*')
def ANIMES_PAGE(animeurl):
    order = control.getSetting('reverseorder')
    episodes = _BROWSER.get_anime_episodes(animeurl, isDirectoryStyle())
    if ("Ascending" in order):
        episodes = reversed(episodes)
    return control.draw_items(episodes)


@route('newest')
def NEWEST(payload):
    return control.draw_items(_BROWSER.get_newest())


@route('newest/*')
def NEWEST_PAGES(payload):
    return control.draw_items(_BROWSER.get_newest(int(payload)))


@route('latest')
def LATEST(payload):
    return control.draw_items(_BROWSER.get_latest())


@route('latest/*')
def LATEST_PAGES(payload):
    return control.draw_items(_BROWSER.get_latest(int(payload)))


@route('recent_subbed')
def SUBBED(payload):
    return control.draw_items(_BROWSER.get_recent_subbed())


@route('recent_subbed/*')
def SUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_recent_subbed(int(payload)))


@route('recent_dubbed')
def DUBBED(payload):
    return control.draw_items(_BROWSER.get_recent_dubbed())


@route('recent_dubbed/*')
def DUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_recent_dubbed(int(payload)))


@route('popular_subbed')
def POPSUBBED(payload):
    return control.draw_items(_BROWSER.get_popular_subbed())


@route('popular_subbed/*')
def POPSUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_popular_subbed(int(payload)))


@route('popular_dubbed')
def POPDUBBED(payload):
    return control.draw_items(_BROWSER.get_popular_dubbed())


@route('popular_dubbed/*')
def POPDUBBED_PAGES(payload):
    return control.draw_items(_BROWSER.get_popular_dubbed(int(payload)))


@route('search')
def SEARCH(payload):
    query = control.keyboard(control.lang(30007))
    if query:
        return control.draw_items(_BROWSER.search_site(query))
    return False


@route('search/*')
def SEARCH_PAGES(payload):
    query, page = payload.rsplit("/", 1)
    return control.draw_items(_BROWSER.search_site(query,
                                                   int(page)))


@route('genres')
def LIST_GENRES(payload):
    return control.draw_items(_BROWSER.get_genres())


@route('genre/*')
def GENRE_ANIMES(payload):
    genre, page = payload.rsplit("/", 1)
    return control.draw_items(_BROWSER.get_genre(genre, int(page)))


@route('play/*')
def PLAY(payload):
    anime_url, episode = payload.rsplit("/", 1)
    sources = _BROWSER.get_episode_sources(anime_url, int(episode))
    anime_name = payload.split(".")[0] + " episode " + episode + " "
    serverChoice = filter(lambda x:
                          control.getSetting(x[0]) == 'true', SERVER_CHOICES.iteritems())
    serverChoice = map(lambda x: x[1], serverChoice)
    sources = filter(lambda x: x[0] in serverChoice, sources)

    autoplay = True if 'true' in control.getSetting('autoplay') else False

    s = SourcesList(sources, autoplay, sortResultsByRes, {
        'title': control.lang(30100),
        'processing': control.lang(30101),
        'choose': control.lang(30102),
        'notfound': control.lang(30103),
    })

    if isDirectoryStyle():
        if s._read_sources():
            items = sorted(s._sources.iteritems(), key=lambda x: x[0])
            items = [(title[5:], url) for title, url in items]
            # items = map(lambda x: utils.allocate_item(x[0], 'playlink&url=/'+x[1], False, ''), items)
            items = map(lambda x: utils.allocate_item(anime_name + x[0], 'playlink/&url=' + x[1], False, ''), items)
            return control.draw_items(items)
    else:
        return control.play_source(s.get_video_link())


@route('playlink/*')
def PLAY_SOURCE(payload):
    par = payload.split("&")
    name = ""
    download = ""
    url = ""
    for p in par[1:]:
        if p.startswith("name"):
            name = p.split("=")[1] + ".mp4"
        if p.startswith("url"):
            url = p.split("=")[1]
        if p.startswith("download"):
            download = p.split("=")[1]
    path = name.split("_")[0]
    if download == "1":
        control.aria2_download(url, name, path)
    else:
        return control.play_source(urlparse.unquote(url))


@route('')
def LIST_MENU(payload):
    return control.draw_items([utils.allocate_item(name, url, True) for name, url in MENU_ITEMS])


# router_process(control.get_plugin_url())
'''
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
    # try:
    #     page = plugin.request.args["page"][0]
    # except KeyError:
    #     page = 1
    plugin.log.info(page)
    animes = _BROWSER.get_latest(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        # u = anime["url"]
        # if not u.startswith("latest"):
        #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        # else:
        #     path = plugin.url_for("latest", page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": url_for(anime["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/animes/<anime>")
def animes(anime):
    plugin.log.info(anime)
    episodes = _BROWSER.get_anime_episodes(anime, isDirectoryStyle())
    plugin.log.info(episodes[0])
    plugin.log.info(episodes[-1])
    items = []
    for episode in episodes:
        # anime, episode_number = episode["url"].split("/")[1:]
        items.append(
            {
                "label": episode["name"],
                # "path": plugin.url_for("play", anime=anime, episode_number=episode_number)
                "path": url_for(episode["url"])
            }
        )
    return plugin.finish(items)
    pass


@plugin.route("/play/<anime>/<episode_number>")
def play(anime, episode_number):
    plugin.log.info("Anime: {} Episode: {}".format(anime, episode_number))

    sources = _BROWSER.get_episode_sources(anime, int(episode_number))
    serverChoice = filter(lambda x:
                          plugin.get_setting(x[0]) == 'true', SERVER_CHOICES.iteritems())
    serverChoice = map(lambda x: x[1], serverChoice)
    sources = filter(lambda x: x[0] in serverChoice, sources)

    autoplay = True if 'true' in plugin.get_setting('autoplay') else False

    s = SourcesList(sources, autoplay, sortResultsByRes, {
        'title': "Fetching Sources",
        'processing': "Processing %s",
        'choose': "Please choose source: ",
        'notfound': "Couldn't find eligible sources",
    })
    #
    # if isDirectoryStyle():
    #     if s._read_sources():
    #         items = sorted(s._sources.iteritems(), key=lambda x: x[0])
    #         items = [(title[5:], url) for title, url in items]
    #         items = map(lambda x: utils.allocate_item(x[0], 'playlink&url='+x[1], False, ''), items)
    #         #items = map(lambda x: utils.allocate_item(anime_name + x[0], 'playlink/&url=' + x[1], False, ''), items)
    #         return control.draw_items(items)
    # else:
    if running_cli:
        return plugin.finish([])
    link = s.get_video_link()
    plugin.log.info("Playlink: " + link)
    item = {"label": anime, "path": link}
    return plugin.play_video(item)


@plugin.route("/newest", name="newest_d", options={"page": "1"})
@plugin.route("/newest/<page>")
def newest(page):
    # try:
    #     page = plugin.request.args["page"][0]
    # except KeyError:
    #     page = 1
    plugin.log.info(page)
    animes = _BROWSER.get_newest(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        # u = anime["url"]
        # if not u.startswith("newest"):
        #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        # else:
        #     path = plugin.url_for("newest", page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": url_for(anime["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/recent_subbed", name="recent_subbed_d", options={"page": "1"})
@plugin.route("/recent_subbed/<page>")
def recent_subbed(page):
    # try:
    #     page = plugin.request.args["page"][0]
    # except KeyError:
    #     page = 1
    plugin.log.info(page)
    animes = _BROWSER.get_recent_subbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        # u = anime["url"]
        # if not u.startswith("recent_subbed"):
        #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        # else:
        #     path = plugin.url_for("recent_subbed", page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": url_for(anime["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/popular_subbed", name="popular_subbed_d", options={"page": "1"})
@plugin.route("/popular_subbed/<page>")
def popular_subbed(page):
    # try:
    #     page = plugin.request.args["page"][0]
    # except KeyError:
    #     page = 1
    plugin.log.info(page)
    animes = _BROWSER.get_popular_subbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        # u = anime["url"]
        # if not u.startswith("popular_subbed"):
        #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        # else:
        #     path = plugin.url_for("popular_subbed", page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": url_for(anime["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/recent_dubbed", name="recent_dubbed_d", options={"page": "1"})
@plugin.route("/recent_dubbed/<page>")
def recent_dubbed(page):
    # try:
    #     page = plugin.request.args["page"][0]
    # except KeyError:
    #     page = 1
    plugin.log.info(page)
    animes = _BROWSER.get_recent_dubbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        # u = anime["url"]
        # if not u.startswith("recent_dubbed"):
        #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        # else:
        #     path = plugin.url_for("recent_dubbed", page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": url_for(anime["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/popular_dubbed", name="popular_dubbed_d", options={"page": "1"})
@plugin.route("/popular_dubbed/<page>")
def popular_dubbed(page):
    # try:
    #     page = plugin.request.args["page"][0]
    # except KeyError:
    #     page = 1
    plugin.log.info(page)
    animes = _BROWSER.get_popular_dubbed(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        # u = anime["url"]
        # if not u.startswith("popular_dubbed"):
        #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        # else:
        #     path = plugin.url_for("popular_dubbed", page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": url_for(anime["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/genres")
def genres():
    genres = _BROWSER.get_genres()
    plugin.log.info(genres[0])
    items = []
    for genre in genres:
        name, page = genre["url"].split("/")[1:]
        items.append(
            {
                "label": genre["name"],
                "path": url_for(genre["url"])
            }
        )
    return plugin.finish(items)
    pass


@plugin.route("/genre/<name>/<page>")
def genre(name, page):
    animes = _BROWSER.get_genre(name, int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        # u = anime["url"]
        # if not u.startswith("genre"):
        #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        # else:
        #     path = plugin.url_for("genre", name=name, page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": url_for(anime["url"])
            }
        )
    return plugin.finish(items)


@plugin.route("/search", name="search_d", options={"query": "", "page": "1"})
@plugin.route("/search/<query>/<page>")
def search(query, page):
    # try:
    #     query = plugin.request.args["query"][0]
    #     page = plugin.request.args["page"][0]
    # except KeyError:
    #     page = 1
    if query == "":
        query = plugin.keyboard(heading="Search Anime")
    plugin.log.info(page)
    if query:
        animes = _BROWSER.search_site(query, int(page))
        plugin.log.info(animes[0])
        plugin.log.info(animes[-1])
        items = []
        for anime in animes:
            u = anime["url"]
            # if not u.startswith("search"):
            #     path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
            # else:
            #     q, p = u.split("/")[1:]
            # path = plugin.url_for("search", query=q, page=p)
            path = url_for(u)
            items.append(
                {
                    "label": anime["name"],
                    "path": url_for(anime["url"])
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
