# from resources.lib.ui import control
from resources.lib.ui import utils
from resources.lib.ui.SourcesList import SourcesList
# from resources.lib.ui.router import route, router_process
from resources.lib.NineAnimeBrowser import NineAnimeBrowser
# import urlparse

from xbmcswift2 import Plugin

plugin = Plugin()
SERVER_CHOICES = {
    "serverg4": "Server G4",
    "serverrapid": "RapidVideo",
    "servermycloud": "MyCloud",
    "serveropenload": "OpenLoad",
}

_BROWSER = NineAnimeBrowser()


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
    ("Latest", "latest"),
    ("Newest", "newest"),
    ("Recent Subbed", "recent_subbed"),
    ("Popular Subbed", "popular_subbed"),
    ("Recent Dubbed", "recent_dubbed"),
    ("Popular Dubbed", "popular_dubbed"),
    ("Genres", "genres"),
    ("Search", "search"),
    ("Settings", "settings")
]


# @plugin.route("/latest", name="default", options={"page": "0"})
@plugin.route("/latest")
def latest():
    try:
        page = plugin.request.args["page"][0]
    except KeyError:
        page = 1
    plugin.log.info(page)
    animes = _BROWSER.get_latest(int(page))
    plugin.log.info(animes[0])
    plugin.log.info(animes[-1])
    items = []
    for anime in animes:
        u = anime["url"]
        if not u.startswith("latest"):
            path = plugin.url_for("animes", anime=anime["url"].split("/")[-1])
        else:
            path = plugin.url_for("latest", page=anime["url"].split("/")[-1])
        items.append(
            {
                "label": anime["name"],
                "path": path
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
        anime, episode_number = episode["url"].split("/")[1:]
        items.append(
            {
                "label": episode["name"],
                "path": plugin.url_for("play", anime=anime, episode_number=episode_number)
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
    link = s.get_video_link()
    plugin.log.info("Playlink: " + link)
    item = {"label": anime, "path": link}
    return plugin.play_video(item)
    # return plugin.finish([])
    pass


@plugin.route("/newest")
def newest():
    pass


@plugin.route("/recent_subbed")
def recent_subbed():
    pass


@plugin.route("/popular_subbed")
def popular_subbed():
    pass


@plugin.route("/recent_dubbed")
def recent_dubbed():
    pass


@plugin.route("/popular_dubbed")
def popular_dubbed():
    pass


@plugin.route("/genres")
def genres():
    pass


@plugin.route("/search")
def search():
    pass


@plugin.route("/settings")
def settings():
    plugin.open_settings()
    pass


@plugin.route('/')
def list_menu():
    items = []
    for name, url in MENU_ITEMS:
        items.append({"label": name, "path": plugin.url_for(url)})
    return items


if __name__ == '__main__':
    plugin.run()
    plugin.set_content("tvshows")
