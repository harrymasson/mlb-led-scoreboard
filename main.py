from datetime import datetime, timedelta
from data.scoreboard_config import ScoreboardConfig
from renderers.main import MainRenderer
from renderers.offday import OffdayRenderer
from renderers.standings import StandingsRenderer
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from utils import args, led_matrix_options
from data.data import Data
import renderers.standings
import mlbgame
import debug

SCRIPT_NAME = "MLB LED Scoreboard"
SCRIPT_VERSION = "2.2.0"

# Get supplied command line arguments
args = args()

# Check for led configuration arguments
matrixOptions = led_matrix_options(args)

# Initialize the matrix
matrix = RGBMatrix(options = matrixOptions)

# Print some basic info on startup
debug.info("{} - v{} ({}x{})".format(SCRIPT_NAME, SCRIPT_VERSION, matrix.width, matrix.height))

# Read scoreboard options from config.json if it exists
config = ScoreboardConfig("config", matrix.width, matrix.height)
debug.set_debug_status(config)

# Create a new data object to manage the MLB data
# This will fetch initial data from MLB
data = Data(config)

# Render the standings or an off day screen
def display_standings(matrix, data):
  try:
    StandingsRenderer(matrix, matrix.CreateFrameCanvas(), data).render()
  except:
    # Out of season off days don't always return standings so fall back on the offday renderer
    OffdayRenderer(matrix, matrix.CreateFrameCanvas(), datetime(data.year, data.month, data.day)).render()

# Check if we should just display the standings
if config.standings_always_display:
	display_standings(matrix, data)

# Otherwise, we'll start displaying games depending on config settings
else:
  # No baseball today.
  if data.is_offday():
    if config.standings_mlb_offday:
      display_standings(matrix, data)
    else:
      OffdayRenderer(matrix, matrix.CreateFrameCanvas(), datetime(data.year, data.month, data.day)).render()

  # Baseball!
  else:
    if config.preferred_teams:
      if data.is_offday_for_preferred_team() and config.standings_team_offday:
        display_standings(matrix, data)
      else:
        MainRenderer(matrix, data).render()
