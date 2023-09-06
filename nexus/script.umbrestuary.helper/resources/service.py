import xbmc, xbmcgui
from threading import Thread
from modules.OMDb import OMDbAPI

logger = xbmc.log
empty_ratings = {'metascore': '', 'tomatoMeter': '', 'tomatoUserMeter': '', 'tomatoImage': '', 'imdbRating': '', 'tmdbRating': ''}

class RatingsService(xbmc.Monitor):
    def __init__(self):
        xbmc.Monitor.__init__(self)
        self.omdb_api = OMDbAPI
        self.window = xbmcgui.Window
        self.get_window_id = xbmcgui.getCurrentWindowId
        self.get_infolabel = xbmc.getInfoLabel
        self.get_visibility = xbmc.getCondVisibility
        self.current_imdb_id = ''

    def listitem_monitor(self):
        while not self.abortRequested():
            
            api_key = self.get_infolabel('Skin.String(omdb_api_key)')
            if not api_key:
                # No API key. Wait 5 seconds and then restart loop.
                logger('###no API key###', 2)
                self.waitForAbort(5)
                continue
            
            if not self.get_visibility('Window.IsVisible(videos) | Window.IsVisible(home)'):
                # The window isn't either video or home window (you can add your search window here too (Window.IsVisible(11121)), as well as eventually info dialogs etc).
                # Wait 2 seconds and then restart loop.
                logger('###Not video or home window###', 2)
                self.waitForAbort(2)
                continue
            
            if self.get_visibility('Container.Scrolling'):
                # The container is scrolling. Wait 0.2 seconds and then restart loop.
                logger('###container is scrolling###', 2)
                self.waitForAbort(0.2)
                continue

            imdb_id = self.get_infolabel('ListItem.IMDBNumber')
            if not imdb_id or not imdb_id.startswith('tt') or imdb_id == self.current_imdb_id:
                # No valid imdb_id key or the same key as current. Wait 0.2 seconds and then restart loop.
                logger('###not valid imdb_id or imdb_id same as current###', 2)
                self.waitForAbort(0.2)
                continue
            
            # Set the imdb_id as current
            self.current_imdb_id = imdb_id

            # Looks like we can look up and set ratings for this listitem. Thread this so the monitor doesn't wait until it has finished to continue.
            Thread(target=self.set_ratings, args=(api_key, imdb_id)).start()
            self.waitForAbort(0.2)


    def set_ratings(self, api_key, imdb_id):
        set_property = self.window(self.get_window_id()).setProperty
        #reset all the values to empty (you might not want to do this)
        for k, v in empty_ratings.items():
            set_property('umbrestuary.%s' % k, v)
        
        # Another small pause (you may not want to do this. If not, then remove the check below for the same imdb_id).
        self.waitForAbort(0.20)
        # Check the same listitem is focused before asking for the ratings. If not a match, don't fetch ratings.
        if imdb_id != self.get_infolabel('ListItem.IMDBNumber'):
            return
        
        result = self.omdb_api().fetch_info({"imdb_id": imdb_id}, api_key)
        logger('###IMDB_ID: %s, RESULT: %s###' % (imdb_id, result), 2)
        if not result: return
        for k, v in result.items():
            # Good idea to not set generic property names i.e. "metacritic" just in case some other skin/addon decides to set the same thing. Always include a unique
            # string in the name, such as skin name/addon name etc.
            set_property('umbrestuary.%s' % k, v)

# Add anything here you want to run as a service
xbmc.log('RatingsService Started', 2)
RatingsService().listitem_monitor()
xbmc.log('RatingsService Finished', 2)
