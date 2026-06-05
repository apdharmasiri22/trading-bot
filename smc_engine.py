class SMCEngine:
    def update(self, candles):

        highs = [c["high"] for c in candles]
        lows = [c["low"] for c in candles]

        if len(highs) < 3:
            return {
                "structure": "NEUTRAL",
                "structure_score": 0
            }

        hh = highs[-1] > highs[-2] > highs[-3]
        hl = lows[-1] > lows[-2] > lows[-3]

        lh = highs[-1] < highs[-2] < highs[-3]
        ll = lows[-1] < lows[-2] < lows[-3]

        if hh and hl:
            return {
                "structure": "BULLISH",
                "structure_score": 30
            }

        elif lh and ll:
            return {
                "structure": "BEARISH",
                "structure_score": 30
            }

        return {
            "structure": "RANGE",
            "structure_score": 10
        }
