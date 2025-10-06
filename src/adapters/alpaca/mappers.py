###
# Last edit: 10/5/25
#
# Desc: Maps broker specific values/strings to uniform values/strings
###

from core.domain.models import Timeframe
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit


#map my domain timeframe to an alpaca timeframe
def map_timeframe(tf: Timeframe) -> str:
    if tf.value == "1Min": return TimeFrame(1, TimeFrameUnit.Minute)
    if tf.value == "5Min": return TimeFrame(5, TimeFrameUnit.Minute)
    if tf.value == "15Min":return TimeFrame(15, TimeFrameUnit.Minute)
    if tf.value == "1H": return TimeFrame(1, TimeFrameUnit.Hour)
    if tf.value == "1D":return TimeFrame(1, TimeFrameUnit.Day)
    raise ValueError(f"Unsupported timeframe: {tf}")