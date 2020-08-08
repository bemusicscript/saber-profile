import re
import json
from attrdict import AttrDict
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse

from app.modules import steam, scoresaber, create_card, user_info


class Tier:
    @csrf_exempt
    def get_tiers(self, request):
        with open("app/modules/json/tier.json") as f:
            tiers = json.loads(f.read())
        return render(request, "tier.html", {"tiers": tiers})
