from plugin_integration.badbanana import run_badbanana
from plugin_integration.own import run_own
from plugin_integration.blackglass import run_blackglass

if __name__ == "__main__":
    sample = ["example1","example2"]
    run_badbanana(sample)
    run_own(sample)
    run_blackglass(sample)
