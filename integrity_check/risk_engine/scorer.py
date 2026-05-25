from config import load_config

class RiskScorer:
    def __init__(self, config_path="config.yaml"):
        self.config = load_config(config_path)
        self.severity_scores = self.config.get('severity_scores', 
                                               {'red':10, 'orange':5, 'yellow':2})
        self.detector_weights = self.config.get('detector_weights', {})

    def score(self, flags: list) -> dict:
        total = 0
        red_count = 0
        orange_count = 0
        for f in flags:
            base = self.severity_scores.get(f.severity, 0)
            weight = self.detector_weights.get(f.risk_type, 1.0)
            total += base * weight
            if f.severity == 'red': red_count += 1
            elif f.severity == 'orange': orange_count += 1

        level = 'LOW_RISK'
        if total >= 15 or (red_count >= 1 and total >= 5):
            level = 'HIGH_RISK'
        elif total >= 6:
            level = 'MEDIUM_RISK'

        return {
            'total_score': total,
            'risk_level': level,
            'red_count': red_count,
            'orange_count': orange_count,
            'flag_summary': len(flags)
        }