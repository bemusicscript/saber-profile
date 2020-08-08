import time
import json
import math
import re

import qrcode
import requests
from attrdict import AttrDict
from bitlyshortener import Shortener

from base.settings import BITLY_API_KEY


class Scoresaber:
    def get_user_data(self, user_id):
        url = f"https://new.scoresaber.com/api/player/{user_id}/full"
        data = requests.get(url)
        return AttrDict(data.json())

    def get_user_data_by_name(self, user_name):
        url = f"https://new.scoresaber.com/api/players/by-name/{user_name}"
        data = requests.get(url)
        return AttrDict(data.json())

    def get_qrcode(self, user_id):
        url = f"https://scoresaber.com/u/{user_id}"
        shortener = Shortener(tokens=BITLY_API_KEY)
        short_url = shortener._shorten_url(url)
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=5,
            border=1,
        )
        qr.add_data(short_url)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white")

    def _get_players(self, page):
        url = f"https://new.scoresaber.com/api/players/{page}"
        return requests.get(url).json()["players"]

    def _check_pp_500_user(self, pp_500_page):
        """
            from players api data.
            is it good? :thinking_face:
        """
        found_flag = False
        prev_player = None
        players_data = self._get_players(pp_500_page)
        for index, player in enumerate(players_data):
            if player["pp"] < 500.001 and player["pp"] > 499.99:
                found_flag = True
                break
            elif player["pp"] < 500.001:
                return self._check_pp_500_user(pp_500_page - 1)
            else:
                prev_player = player

        if found_flag is True:
            """
                return to found_page, user_rank 
            """
            return pp_500_page, prev_player["rank"]
        else:
            return self._check_pp_500_user(pp_500_page + 1)

    def get_pp_500_rank(self):
        json_path = "app/modules/json/user_info.json"
        with open(json_path) as f:
            ori_data = json.loads(f.read())
        pp_500_page = ori_data["pp_500_page"]
        while True:
            try:
                _page, _rank = self._check_pp_500_user(pp_500_page)
                break
            except Exception as e:
                print(e)
                time.sleep(1)

        ori_data.update({"pp_500_page": _page, "pp_500_rank": _rank})
        with open(json_path, "w") as f:
            json.dump(ori_data, f, indent=4, sort_keys=True)
        return _page, _rank

    def get_player_by_rank(self, rank):
        page = math.ceil(rank / 50)
        for player in self._get_players(page):
            if player["rank"] == rank:
                return player
