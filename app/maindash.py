import dash
import diskcache
from dash.long_callback import DiskcacheLongCallbackManager

long_callback_manager = DiskcacheLongCallbackManager(cache)
cache = diskcache.Cache("cache")
app = Dash(__name__, external_stylesheets=external_stylesheets, long_callback_manager=long_callback_manager)
