import os
import base64
import json
from attrdict import AttrDict
from datetime import date
from io import BytesIO
from PIL import Image, ImageDraw, ImageOps, ImageFont

from .scoresaber import Scoresaber
from .steam import Steam
from .config import *


class CreateCard:
    def __init__(self):
        self.steam = Steam()
        self.scoresaber = Scoresaber()

    def save_card(self, image):
        try:
            card_path = f"{PROFILE_IMAGE_PATH}/{self.user_data.id}.png"
            image.save(card_path)
            return card_path
        except Exception as e:
            print(e)
            return None

    def get_card(self):
        card = self.render_card()
        return self.save_card(card)

    def render_card(self):
        self.font = f"{FONT_PATH}/Lato-Black.ttf"
        self.text_color = (13, 13, 13)
        self.outline_color = (175, 171, 171)
        w_margin, h_margin = (40, 20)

        bg = self.render_background()
        self.draw = ImageDraw.Draw(bg)
        bg_w, bg_h = bg.size

        """ Banner """
        banner = self.render_banner()
        bg.paste(banner, (w_margin - 30, h_margin), banner)

        """ Propic """
        propic = self.render_propic()
        bg.paste(propic, (w_margin, 100), propic)

        """ Flag """
        flag = self.render_country_flag()
        bg.paste(flag, (w_margin, 100))

        """ Rank text """
        text, font = self.render_rank_title()
        text_w, _ = self.draw.textsize(text, font)
        text_w, text_h = (bg_w - text_w - w_margin, h_margin + 12)
        self._text_outliner(
            text_w,
            text_h,
            text,
            font,
            custom_outline_color=(255, 255, 255),
            outline_size=2,
        )

        """ Player name text """
        text, font = self.render_username_title()
        text_w, text_h = (
            w_margin + propic.size[0] + 20,
            h_margin + banner.size[1] - 10,
        )
        self._text_outliner(text_w, text_h, text, font, outline_size=2)

        text, font = self.render_username_text()
        text_w, _ = self.draw.textsize(text, font)
        text_w, text_h = (bg_w - text_w - w_margin, h_margin + banner.size[1] + 20)
        self._text_outliner(
            text_w,
            text_h,
            text,
            font,
            custom_outline_color=(255, 255, 255),
            outline_size=2,
        )

        """ Tier Data """
        text, font = self.render_tier_title()
        text_w, text_h = (
            w_margin + propic.size[0] + 20,
            h_margin + banner.size[1] + 50,
        )
        self._text_outliner(text_w, text_h, text, font, outline_size=2)

        """ Tier text """
        tier, tier_color = self._get_user_tier()
        font = ImageFont.truetype(self.font, 22)
        text_w, _ = self.draw.textsize(tier, font)
        text_w, text_h = (bg_w - text_w - w_margin, h_margin + banner.size[1] + 80)
        self._text_outliner(
            text_w,
            text_h,
            tier,
            font,
            custom_outline_color=tuple(tier_color),
            outline_size=2,
        )

        """ Tier sub text """
        text, font = self.render_tier_text(self.user_info.rate)
        text_w, _ = self.draw.textsize(text, font)

        text_w, text_h = (bg_w - text_w - w_margin, h_margin + banner.size[1] + 110)
        self._text_outliner(
            text_w,
            text_h,
            text,
            font,
            custom_outline_color=(255, 255, 255),
            outline_size=2,
        )

        """ Draw QRCode """
        qr = self.render_qrcode()
        w, h = qr.size
        bg.paste(qr, (bg_w - w - w_margin, bg_h - h - h_margin - 5), qr)

        """ Draw Last updated date """
        text, font = self.render_created_date()
        self.draw.text((268, 300), text, font=font, fill=self.outline_color)
        return bg

    def set_user_data(self, user_data, user_info):
        """
            user_info parameter is used to obtain current tier info.
        """
        self.user_info = AttrDict(user_info)
        self.user_data = AttrDict(user_data)
        self.score_user = self.scoresaber.get_user_data(self.user_data.id)

    def render_background(self, width=608, height=342):
        """ render background card image """
        img_path = IMG_PATH + os.sep + CARD_BACKGROUND
        bg_img = Image.open(img_path)
        bg_img = bg_img.resize((width, height))
        bg_img = self._add_corners(bg_img, rad=30)
        return bg_img

    def render_propic(self):
        """ propic size is fixed to 184*184 """
        if self.user_data.platform == "steam":
            propic_data = self.steam.get_user_propic(user_id=self.user_data.id)
        else:
            propic_data = open("app/modules/img/oculus.png", "rb")
        propic = Image.open(propic_data)
        propic = propic.convert("RGBA")
        propic = self._add_corners(propic, rad=30)
        return propic

    def render_country_flag(self, width=40, height=27):
        """ render country flag image """
        try:
            flag_sign = self.user_info.country
        except:
            flag_sign = "unk"
        flag_path = f"{IMG_FLAG_PATH}/{flag_sign}.png"
        flag_img = Image.open(flag_path)
        flag_img = flag_img.resize((width, height))
        return flag_img

    def render_banner(self, width=300, height=85):
        """ render saber profile banner image """
        img_path = IMG_PATH + os.sep + CARD_BANNER
        banner_img = Image.open(img_path)
        banner_img = banner_img.resize((width, height))
        return banner_img

    def render_qrcode(self, width=50, height=50):
        """ render qrcode to user's scoresaber page link """
        qr = self.scoresaber.get_qrcode(self.user_data.id)
        qr = qr.resize((width, height))
        return qr

    def render_username_title(self, font_size=26):
        text = "PLAYER"
        font = ImageFont.truetype(self.font, font_size)
        return text, font

    def render_username_text(self, font_size=24):
        text = self.user_data.name
        font = ImageFont.truetype(f"{FONT_PATH}/Spoqa Han Sans Bold.ttf", font_size)
        return text, font

    def render_rank_title(self, font_size=40):
        text = f"#{self.score_user.playerInfo.rank}"
        font = ImageFont.truetype(self.font, font_size)
        return text, font

    def render_tier_title(self, font_size=26):
        text = "TIER"
        font = ImageFont.truetype(self.font, font_size)
        return text, font

    def render_tier_text(self, user_rate, font_size=18):
        text = f"{self.score_user.playerInfo.pp} PP  ( Top {user_rate:.04f}% Player )"
        font = ImageFont.truetype(self.font, font_size)
        return text, font

    def render_created_date(self, font_size=15):
        font = ImageFont.truetype(self.font, font_size)
        return str(date.today()), font

    def _get_user_tier(self):
        tier = self.user_info.tier
        rate = self.user_info.rate

        with open("app/modules/json/tier.json") as f:
            user_json = json.loads(f.read())
        data = user_json[tier]
        return data["name"], data["color"]

    def _text_outliner(
        self, x, y, text, font, custom_outline_color=None, outline_size=1
    ):
        if custom_outline_color:
            o_color = custom_outline_color
        else:
            o_color = self.outline_color
        v = outline_size

        # thin border
        self.draw.text((x - v, y), text, font=font, fill=o_color)
        self.draw.text((x + v, y), text, font=font, fill=o_color)
        self.draw.text((x, y - v), text, font=font, fill=o_color)
        self.draw.text((x, y + v), text, font=font, fill=o_color)

        # thicker border
        self.draw.text((x - v, y - v), text, font=font, fill=o_color)
        self.draw.text((x + v, y - v), text, font=font, fill=o_color)
        self.draw.text((x - v, y + v), text, font=font, fill=o_color)
        self.draw.text((x + v, y + v), text, font=font, fill=o_color)

        self.draw.text((x, y), text, font=font, fill=self.text_color)

    def _add_corners(self, img, rad):
        circle = Image.new("L", (rad * 2, rad * 2), 0)
        draw = ImageDraw.Draw(circle)
        draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
        alpha = Image.new("L", img.size, 255)
        w, h = img.size
        alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
        alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
        alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
        alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
        img.putalpha(alpha)
        return img

    def _change_contrast(self, img, level):
        factor = (259 * (level + 255)) / (255 * (259 - level))

        def contrast(c):
            return 128 + factor * (c - 128)

        return img.point(contrast)
