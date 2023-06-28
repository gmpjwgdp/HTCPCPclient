import views
from coffie.urls.pattern import URLPattern

# pathとview関数の対応
url_patterns = [
    URLPattern("/pot/<prop>", views.pot),
    URLPattern("/cup/<prop>", views.cup),
    URLPattern("/milk/stop", views.stop_milk),
    URLPattern("/coffie/brew", views.brew_coffie),
    URLPattern("/tea/brew", views.brew_tea),
]