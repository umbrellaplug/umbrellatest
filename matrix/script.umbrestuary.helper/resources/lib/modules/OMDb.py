import xbmc, xbmcvfs
import datetime as dt
import xml.etree.ElementTree as ET
import sqlite3 as database
import requests
import json

settings_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.umbrestuary.helper/"
)
ratings_database_path = xbmcvfs.translatePath(
    "special://profile/addon_data/script.umbrestuary.helper/ratings_cache.db"
)


def make_session(url="https://"):
    session = requests.Session()
    session.mount(url, requests.adapters.HTTPAdapter(pool_maxsize=100))
    return session


url = "http://www.omdbapi.com/?apikey=%s&i=%s&tomatoes=True&r=xml"
session = make_session("http://www.omdbapi.com/")


class OMDbAPI:
    # last_checked_imdb_id = None

    def __init__(self):
        self.connect_database()

    def connect_database(self):
        if not xbmcvfs.exists(settings_path):
            xbmcvfs.mkdir(settings_path)
        self.dbcon = database.connect(ratings_database_path, timeout=20)
        self.dbcon.execute(
            """
        CREATE TABLE IF NOT EXISTS ratings (
            imdb_id TEXT PRIMARY KEY,
            ratings TEXT,
            last_updated TIMESTAMP
        );
        """
        )
        self.dbcur = self.dbcon.cursor()

    def insert_or_update_ratings(self, imdb_id, ratings):
        self.dbcur.execute("SELECT imdb_id FROM ratings WHERE imdb_id=?", (imdb_id,))
        entry = self.dbcur.fetchone()
        ratings_data = json.dumps(ratings)
        if entry:
            self.dbcur.execute(
                """
            UPDATE ratings 
            SET ratings=?, last_updated=?
            WHERE imdb_id=?
            """,
                (ratings_data, dt.datetime.now(), imdb_id),
            )
        else:
            self.dbcur.execute(
                """
            INSERT INTO ratings (imdb_id, ratings, last_updated)
            VALUES (?, ?, ?)
            """,
                (imdb_id, ratings_data, dt.datetime.now()),
            )
        self.dbcon.commit()

    def get_cached_ratings(self, imdb_id):
        self.dbcur.execute(
            "SELECT imdb_id, ratings, last_updated FROM ratings WHERE imdb_id=?",
            (imdb_id,),
        )
        entry = self.dbcur.fetchone()
        if entry:
            _, ratings_data, last_updated = entry
            ratings = json.loads(ratings_data)
            if dt.datetime.now() - dt.datetime.strptime(
                last_updated, "%Y-%m-%d %H:%M:%S.%f"
            ) < dt.timedelta(days=7):
                return ratings
        return None

    def fetch_info(self, meta, api_key):
        imdb_id = meta.get("imdb_id")
        if not imdb_id or not api_key:
            return {}
        cached_ratings = self.get_cached_ratings(imdb_id)
        if cached_ratings:
            return cached_ratings
        data = self.get_result(imdb_id, meta)
        self.insert_or_update_ratings(imdb_id, data)
        return data

    def get_result(self, imdb_id, api_key):
        api_key = xbmc.getInfoLabel("Skin.String(omdb_api_key)")
        if not api_key:
            # xbmc.log("No OMDb API key set in the skin settings.", level=xbmc.LOGERROR)
            return {}
        url = (
            f"http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}&tomatoes=True&r=xml"
        )
        # xbmc.log(
        #     "Fetching fresh ratings for IMDb ID {} from the OMDb API.".format(imdb_id),
        #     level=xbmc.LOGDEBUG,
        # )
        response = session.get(url)
        if response.status_code != 200:
            # xbmc.log(
            #     f"Error fetching data from OMDb for IMDb ID {imdb_id}. Status code: {response.status_code}"
            # )
            return {}
        root = ET.fromstring(response.content)
        data = root.find("movie")
        if data is None:
            return {}
        tmdb_rating = xbmc.getInfoLabel("ListItem.Rating")
        data = {
            "metascore": (data.get("metascore") + "%" if data.get("metascore") else "")
            if data.get("metascore") != "N/A"
            else "",
            "tomatoMeter": (
                data.get("tomatoMeter") + "%" if data.get("tomatoMeter") else ""
            )
            if data.get("tomatoMeter") != "N/A"
            else "",
            "tomatoUserMeter": (
                data.get("tomatoUserMeter") + "%" if data.get("tomatoUserMeter") else ""
            )
            if data.get("tomatoUserMeter") != "N/A"
            else "",
            "tomatoImage": data.get("tomatoImage")
            if data.get("tomatoImage") != "N/A"
            else "",
            "imdbRating": data.get("imdbRating")
            if data.get("imdbRating") != "N/A"
            else "",
            "tmdbRating": tmdb_rating if tmdb_rating != "N/A" else "",
        }
        return data


def test_api():
    # xbmc.log("test_api function triggered!", level=xbmc.LOGDEBUG)
    api_key = xbmc.getInfoLabel("Skin.String(omdb_api_key)")
    imdb_id = xbmc.getInfoLabel("ListItem.IMDBNumber")
    # if imdb_id == OMDbAPI.last_checked_imdb_id:
    #     return
    if not api_key:
        # xbmc.log("No OMDb API key set in the skin settings.", level=xbmc.LOGDEBUG)
        return {}
    if not imdb_id or not imdb_id.startswith("tt"):
        # xbmc.log(
        #     "Could not retrieve a valid IMDb ID from the focused item.",
        #     level=xbmc.LOGDEBUG,
        # )
        return {}
    omdb_api_instance = OMDbAPI()
    result = omdb_api_instance.fetch_info({"imdb_id": imdb_id}, api_key)
    rating_properties_dict = {
        "Metascore": "metascore",
        "TomatoMeter": "tomatoMeter",
        "TomatoUserMeter": "tomatoUserMeter",
        "IMDbRating": "imdbRating",
        "TMDbRating": "tmdbRating",
    }

    for rating_property_name, result_key in rating_properties_dict.items():
        rating_value = result.get(result_key)
        if rating_value:
            xbmc.executebuiltin(f"SetProperty({rating_property_name}, {rating_value})")
            # xbmc.log(
            #     f"Setting property: {rating_property_name} with value: {rating_value}",
            #     level=xbmc.LOGDEBUG,
            # )
    # xbmc.log(f"Ratings for IMDb ID {imdb_id}: {result}", level=xbmc.LOGDEBUG)
    # OMDbAPI.last_checked_imdb_id = imdb_id
    return result
