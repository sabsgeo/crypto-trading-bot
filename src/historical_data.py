import json

import talib
import numpy

from constants import all_constants
from config import all_configs


class HistoricalData():
    currency = ''
    current_price = 0.0
    max_array_size = 500
    twelve_hrs_in_min = 720

    def __init__(self):
        self.open_times = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.openes = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.highs = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.lows = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.closes = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.volumes = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.close_times = dict(all_constants.EMPTY_UNIT_ARRAY)

        self.latest_rsi = dict(all_constants.EMPTY_UNIT_DICT)
        self.close_count = 0

    def initilize_candle_data(self, candle_data, unit_time):
        self.open_times[unit_time], self.openes[unit_time], self.highs[unit_time], self.lows[unit_time], self.closes[unit_time], self.volumes[unit_time], self.close_times[unit_time] = map(
            lambda each_hist: (each_hist[0], float(each_hist[1]), float(each_hist[2]), float(each_hist[3]), float(each_hist[4]), float(each_hist[5]), each_hist[6]), candle_data)

    def reset_all_data(self):
        self.open_times = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.openes = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.highs = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.lows = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.closes = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.volumes = dict(all_constants.EMPTY_UNIT_ARRAY)
        self.close_times = dict(all_constants.EMPTY_UNIT_ARRAY)

        self.latest_rsi = dict(all_constants.EMPTY_UNIT_DICT)
        self.close_count = 0

    def update_candle_data(self, candle_data, unit_time):
        reset_history = False
        # Making sure with 1m we are always on tack with 12 hrs
        # This helps in reset after 12 hrs
        if (self.close_times[-1] == candle_data['T'] and self.open_times[-1] == candle_data['t']):
            print("Omiting a data entry as data is present")
        elif (self.close_times[-1] - candle_data['T'] != all_configs.TECHNICAL_INDICATOR_CONF.get("TIME_WINDOW_IN_MSEC").get(unit_time) and self.open_times[-1] - candle_data['t'] != all_configs.TECHNICAL_INDICATOR_CONF.get("TIME_WINDOW_IN_MSEC").get(unit_time)):
            print("Data is getting reset")
            reset_history = True
        elif (self.close_times[-1] != candle_data['T'] and self.open_times[-1] != candle_data['t']):
            if unit_time == all_constants.ONE_MIN_STRING:
                self.close_count = self.close_count + 1

            if (len(self.closes[unit_time]) == self.max_array_size):
                self.open_times[unit_time].pop(0)
                self.openes[unit_time].pop(0)
                self.highs[unit_time].pop(0)
                self.lows[unit_time].pop(0)
                self.closes[unit_time].pop(0)
                self.volumes[unit_time].pop(0)
                self.close_times[unit_time].pop(0)

            self.open_times[unit_time].append(candle_data['t'])
            self.openes[unit_time].append(float(candle_data['o']))
            self.highs[unit_time].append(float(candle_data['h']))
            self.lows[unit_time].append(float(candle_data['l']))
            self.closes[unit_time].append(float(candle_data['c']))
            self.volumes[unit_time].append(float(candle_data['v']))
            self.close_times[unit_time].append(candle_data['T'])

            if ((unit_time == all_constants.ONE_MIN_STRING and self.close_count % self.twelve_hrs_in_min == 0) or reset_history):
                self.close_count = 0

    def update_latest_rsi(self, unit_time):
        for each_rsi in all_configs.TECHNICAL_INDICATOR_CONF.get("RSI").get('period'):
            if len(self.closes[unit_time]) > each_rsi:
                np_closes = numpy.array(self.closes[unit_time])
                rsi = talib.RSI(np_closes, each_rsi)
                self.latest_rsi[unit_time][each_rsi] = rsi[-1]

    def update_latest_macd(self, unit_time):
        FAST_P = all_configs.TECHNICAL_INDICATOR_CONF.get(
            "MACD").get("MACD_FAST")
        SLOW_P = all_configs.TECHNICAL_INDICATOR_CONF.get(
            "MACD").get("MACD_SLOW")
        MACD_SIG = all_configs.TECHNICAL_INDICATOR_CONF.get(
            "MACD").get("MACD_SIGNAL")
        if (len(self.closes[unit_time]) > all_configs.TECHNICAL_INDICATOR_CONF.get("MACD").get("MACD_SLOW")):
            np_closes = numpy.array(self.closes[unit_time])
            analysis = talib.MACD(
                np_closes, fastperiod=FAST_P, slowperiod=SLOW_P, signalperiod=MACD_SIG)
            print(analysis)
