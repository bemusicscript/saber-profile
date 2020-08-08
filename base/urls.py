from django.views.generic import TemplateView
from django.conf.urls import url
from django.urls import path

from app.views import Index, Tier, Level, User

urlpatterns = [
    path("", Index.index, name="index"),
    path("about", Index.about, name="about"),
    path("level", Level.index, name="level_index"),
    path("tier", Tier().get_tiers, name="tier_index"),
    path("u/<int:uid>", User().get_propic, name="user_profile"),
    path("api/user/search", User().search_id, name="user_search"),
    path("api/user/get_data", User().get_data, name="user_get_data"),
]

urlpatterns += [
    url(
        r"^robots.txt$",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots",
    ),
]
