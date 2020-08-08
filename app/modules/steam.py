import json

import requests
from attrdict import AttrDict

from base.settings import STEAM_API_KEY


class Steam:
    def __init__(self):
        self.key = STEAM_API_KEY

    def is_steam_id64(self, id_value):
        if len(id_value) == 17 and id_value.isdigit():
            return True
        else:
            return False

    def get_user_data(self, user_id):
        return AttrDict(self.get_user_summary(user_id))

    def get_user_summary(self, user_id):
        url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={api_key}&steamids={steam_id}"
        result = requests.get(url=url.format(api_key=self.key, steam_id=user_id))
        result = result.json()["response"]["players"][0]
        return AttrDict(result)

    def get_user_id(self, vanity_name):
        url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={api_key}&vanityurl={vanity_name}"
        result = requests.get(url=url.format(api_key=self.key, vanity_name=vanity_name))
        result = result.json()
        if result["response"]["success"] == 1:
            return result["response"]["steamid"]
        else:
            return None

    def get_user_propic(self, user_id):
        """ user_id is must be STEAM ID64 Type """
        info = self.get_user_summary(user_id)
        res = requests.get(info["avatarfull"], stream=True)
        return res.raw
