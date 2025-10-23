"""
Shenron integration for Decoy-Hunter
"""

from shenron_integration.utils import analyze_targets
import sys

def run_shenron_in_decoyhunter(targets):
    print("[*] Running Shenron analytics...")
    results = analyze_targets(targets)
    print("[*] Analysis complete")
    for r in results:
        print(f"Target: {r['target']} | Score: {r['shenron_score']}")
    return results

# CLI test
if __name__ == "__main__":
    sample_targets = ["decoy1", "decoy2", "decoy3"]
    run_shenron_in_decoyhunter(sample_targets)
