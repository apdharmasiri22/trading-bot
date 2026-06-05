class ScoreEngine:
    def __init__(self):
        self.scores = {
            "structure": 0,
            "liquidity": 0,
            "entry": 0,
            "pattern": 0,
            "wave": 0,
            "timing": 0
        }

    def update_scores(self, analysis):
        """
        analysis = dict from all engines
        """

        self.scores["structure"] = analysis.get("structure_score", 0)
        self.scores["liquidity"] = analysis.get("liquidity_score", 0)
        self.scores["entry"] = analysis.get("entry_score", 0)
        self.scores["pattern"] = analysis.get("pattern_score", 0)
        self.scores["wave"] = analysis.get("wave_score", 0)
        self.scores["timing"] = analysis.get("timing_score", 0)

        return self.calculate_total()

    def calculate_total(self):
        total = (
            self.scores["structure"] +
            self.scores["liquidity"] +
            self.scores["entry"] +
            self.scores["pattern"] +
            self.scores["wave"] +
            self.scores["timing"]
        )

        return {
            "scores": self.scores,
            "total_score": total,
            "decision": self.get_decision(total)
        }

    def get_decision(self, score):
        if score >= 70:
            return "🟢 HIGH PROBABILITY TRADE (BUY/SELL OK)"
        elif score >= 50:
            return "🟡 WAIT / RISKY TRADE"
        else:
            return "🔴 NO TRADE"
