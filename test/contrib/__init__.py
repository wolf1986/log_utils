import warnings

# Suppress warning from plotly
warnings.filterwarnings(
    'ignore',
    message='Using or importing the ABCs from.*',
    module='plotly.grid_objs'
)
