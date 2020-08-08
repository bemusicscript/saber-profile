import json


class UserInfo:
    def __init__(self, user):
        self.player = user.playerInfo
        self.score = user.scoreStats
        self._load_exps_json()
        self._set_base_data()

    def _load_exps_json(self):
        """ load exps.json """
        with open("app/modules/json/user_info.json") as f:
            try:
                self.user_info_jdat = json.loads(f.read())
                self.exps = self.user_info_jdat["exps"]
            except:
                self.exps = None

    def save(self, path="static/json/user"):
        with open(f"{path}/{self.player.playerId}.json", "w") as f:
            json.dump(self.info, f)

    def _set_base_data(self):
        self.info = {
            "name": self.player.playerName,
            "id": self.player.playerId,
            "tier": 0,
            "tier_name": None,
            "rate": 0.0,
            "country": self.player.country.lower(),
            "rank": {
                "global": self.player.rank,
                "country": self.player.countryRank,
                "history": self.player.history,
            },
            "pp": {"pp": self.player.pp, "min_pp": 0, "max_pp": 0},
            "level": {"level": 0, "exp": 0, "min_exp": 0, "max_exp": 0},
            "scores": {
                "total": {
                    "total_score": self.score.totalScore,
                    "play_count": self.score.totalPlayCount,
                },
                "ranked": {
                    "total_score": self.score.totalRankedScore,
                    "play_count": self.score.rankedPlayCount,
                    "avg_accuracy": f"{self.score.averageRankedAccuracy:.02f}",
                },
            },
        }
        self._set_tier()
        self._set_level()
        self._set_pp_values()

    def _get_user_level(self, user_exp):
        """ return to level, level_req_exp """
        for level, exp in enumerate(self.exps):
            if user_exp < exp:
                return level + 1, exp, self.exps[level - 1]
        return 100, len(self.exps) + 1, 0  # maximum level

    def _calc_user_exp(self, rank_bonus=0.1024):
        normal_score = self.score.totalScore - self.score.totalRankedScore
        ranked_score = self.score.totalRankedScore + (
            self.score.totalRankedScore * rank_bonus
        )
        user_exp = int(normal_score + ranked_score)
        return user_exp

    def _set_level(self):
        """ calculate user exp to level """
        user_exp = self._calc_user_exp()
        level, max_exp, min_exp = self._get_user_level(user_exp)
        self.info.update(
            {
                "level": {
                    "level": level,
                    "exp": user_exp,
                    "max_exp": max_exp,
                    "min_exp": min_exp,
                }
            }
        )

    def _get_user_tier(self, pp_500_rank):
        tier_count = len(self.tiers)
        player_rate = (self.player.rank / pp_500_rank) * 100
        if self.player.rank == 0:
            return 100.0, "0"
        if self.player.rank > pp_500_rank:
            """ Unranked """
            return 100.0, "0"
        elif self.player.rank < 4:
            """ Top Rank """
            return player_rate, "1"

        for tier in range(2, tier_count):
            if tier < 2:
                continue
            if player_rate < self.tiers[str(tier)]["rate"]:
                return player_rate, str(tier)

    def _set_tier(self):
        with open("app/modules/json/tier.json") as f:
            self.tiers = json.loads(f.read())

        pp_500_rank = self.user_info_jdat["pp_500_rank"]
        rate, tier = self._get_user_tier(pp_500_rank)
        name = self.tiers[tier]["name"]
        self.info.update(
            {"tier": tier, "tier_name": name, "rate": float(f"{rate:.04f}")}
        )

    def _set_pp_values(self):
        tier = int(self.info["tier"])
        if tier == 0:
            """ UNRANKED """
            pp_val = {"min_pp": 0, "max_pp": 500}
        elif tier == 1:
            """ MASTER OF SABERS """
            pp_val = {"min_pp": self.tiers["2"]["min_pp"], "max_pp": self.player.pp}
        elif tier == 2:
            pp_val = {"min_pp": self.tiers["3"]["min_pp"], "max_pp": self.player.pp}
        else:
            pp_val = {
                "min_pp": self.tiers[str(tier)]["min_pp"],
                "max_pp": int(self.tiers[str(tier - 1)]["min_pp"]),
            }
        pp_val.update({"pp": self.player.pp})
        self.info.update({"pp": pp_val})
