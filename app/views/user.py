import re
import json
from attrdict import AttrDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from app.modules import steam, scoresaber, create_card, user_info


class User:
    def __init__(self):
        self.steam = steam.Steam()
        self.card = create_card.CreateCard()
        self.scoresaber = scoresaber.Scoresaber()

    def _check_url_type(self, url_value):
        if data := re.search(r"^https?\:\/\/scoresaber.com/u/(\d{16,17})", url_value):
            return data.group(1)
        else:
            return url_value

    def _get_user_data(self, user_id, is_player_id=False, get_info=False):
        if is_player_id:
            ori_data = self.scoresaber.get_user_data(user_id)
            data = ori_data.playerInfo
        else:
            try:
                ori_data = self.scoresaber.get_user_data_by_name(user_id)
                data = ori_data.players[0]
            except:
                return None

        player_id = data.playerId
        if len(player_id) == 17:
            # steam id
            _user = self.steam.get_user_summary(player_id)
            if "loccountrycode" not in _user:
                user_data = {"loc": "UNK"}
            else:
                user_data = {"loc": _user.loccountrycode}
            user_data.update(
                {
                    "profile_image": _user.avatarfull,
                    "id": _user.steamid,
                    "name": _user.personaname,
                    "platform": "steam",
                }
            )
        else:
            user_data = {
                "profile_image": "/static/img/oculus.png",
                "id": data.playerId,
                "name": data.playerName,
                "loc": data.country,
                "platform": "oculus",
            }
        if get_info:
            uinfo = user_info.UserInfo(ori_data)
            uinfo.info.update({"profile_image": user_data["profile_image"]})
            uinfo_data = uinfo.info
            uinfo.save()
            return uinfo_data, user_data
        return user_data

    @csrf_exempt
    def search_id(self, request):
        user_id = request.POST.get("user_id")
        if len(user_id) > 48 and not user_id.startswith("https://"):
            value = None
        if user_id.startswith("https://"):
            user_id = self._check_url_type(user_id)
            user_data = self._get_user_data(user_id, is_player_id=True)
        else:
            user_id = self._check_url_type(user_id)
            user_data = self._get_user_data(user_id)

        return JsonResponse({"result": user_data}, safe=False)

    @csrf_exempt
    def get_data(self, request):
        player_id = request.POST.get("player_id")
        u_info, user_data = self._get_user_data(
            player_id, is_player_id=True, get_info=True
        )
        self.card.set_user_data(user_data, u_info)
        path = self.card.get_card()

        return JsonResponse({"path": path, "id": player_id}, safe=False)

    def get_propic(self, request, uid):
        with open(f"static/json/user/{uid}.json", "r") as f:
            user_info = json.loads(f.read())

        return render(request, "user.html", {"uid": uid, "info": user_info})
