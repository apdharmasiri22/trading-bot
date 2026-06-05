from score_engine import ScoreEngine

score_engine = ScoreEngine()

analysis = {
    "structure_score": 25,
    "liquidity_score": 15,
    "entry_score": 18,
    "pattern_score": 10,
    "wave_score": 7,
    "timing_score": 5
}

result = score_engine.update_scores(analysis)

print("📊 Total Score:", result["total_score"])
print("🎯 Decision:", result["decision"])
