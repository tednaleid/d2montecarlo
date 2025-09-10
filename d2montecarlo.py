#!/usr/bin/env -S uv run --script
import argparse
import random
import statistics
from typing import List, Tuple


def get_power_bumps(
    account_power: int, progression_rules: List[Tuple[int, int, int]]
) -> Tuple[int, int]:
    """
    Get power bump values based on current account power and progression rules.

    Args:
        account_power: Current account power level
        progression_rules: List of (threshold, power_bump, prime_bump) tuples
                          ordered from highest to lowest threshold

    Returns:
        tuple: (power_bump, prime_bump)
    """
    for threshold, power_bump, prime_bump in progression_rules:
        if account_power >= threshold:
            return power_bump, prime_bump
    # Default fallback (shouldn't happen with proper rules)
    return progression_rules[-1][1], progression_rules[-1][2]


def run_simulation(
    power_cap=550, starting_power=400, target_power=550, prime_chance=0.075, progression_rules=None
):
    """
    Run a single simulation of power progression.

    Args:
        power_cap: Target power level to reach
        starting_power: Initial power level for all gear
        target_power: Power level to stop running activities
        prime_chance: Probability of getting a prime drop
        progression_rules: List of (threshold, power_bump, prime_bump) tuples

    Returns:
        tuple: (activity_count, prime_count, final_gear_state)
    """
    # Default progression rules (original scenario)
    if progression_rules is None:
        progression_rules = [
            (400, 0, 3),  # At 400+: power_bump=0, prime_bump=3
            (297, 3, 4),  # At 297+: power_bump=3, prime_bump=4
            (196, 4, 5),  # At 196+: power_bump=4, prime_bump=5
            (0, 6, 7),  # Below 196: power_bump=6, prime_bump=7
        ]

    activity_count = 0
    prime_count = 0
    gear = [starting_power for _ in range(8)]
    account_power = sum(gear) // 8

    while account_power < target_power:
        activity_count += 1
        power_bump, prime_bump = get_power_bumps(account_power, progression_rules)

        if random.random() <= prime_chance:
            prime_count += 1
            slot = random.randrange(8)
            gear[slot] = min(max(account_power + prime_bump, gear[slot]), power_cap)

        slot = random.randrange(8)
        gear[slot] = min(max(account_power + power_bump, gear[slot]), power_cap)

        # primes are rolled at the same time as the regular drop so we don't bump account power till after both drop
        account_power = sum(gear) // 8

    return activity_count, prime_count, gear


def run_scenario_analysis(
    N, scenario_name, power_cap, starting_power, target_power, prime_chance, progression_rules
):
    """Run N simulations for a specific scenario and return statistics."""
    activity_counts = []
    prime_counts = []

    for _ in range(N):
        activities, primes, _ = run_simulation(
            power_cap, starting_power, target_power, prime_chance, progression_rules
        )
        activity_counts.append(activities)
        prime_counts.append(primes)

    return {
        "name": scenario_name,
        "activity_mean": statistics.mean(activity_counts),
        "activity_median": statistics.median(activity_counts),
        "activity_stdev": statistics.stdev(activity_counts),
        "activity_min": min(activity_counts),
        "activity_max": max(activity_counts),
        "activity_25th": statistics.quantiles(activity_counts, n=4)[0],
        "activity_75th": statistics.quantiles(activity_counts, n=4)[2],
        "prime_mean": statistics.mean(prime_counts),
        "prime_median": statistics.median(prime_counts),
        "prime_rate": sum(prime_counts) / sum(activity_counts),
    }


# Parse command-line arguments
parser = argparse.ArgumentParser(
    description="Monte Carlo simulation for Destiny 2 power level progression"
)
parser.add_argument(
    "--starting-power",
    type=int,
    default=400,
    help="Starting power level (default: 400, min: 10, max: power_cap-1)",
)
parser.add_argument(
    "--target-power",
    type=int,
    default=450,
    help="Target power level (default: 550, min: 10, max: power_cap)",
)
args = parser.parse_args()

# Configuration
N = 10000
power_cap = 550
target_power = args.target_power
starting_power = args.starting_power
prime_chance = 0.075

# Validate starting_power
if starting_power < 10:
    print(f"Error: starting_power ({starting_power}) must be at least 10")
    exit(1)
if starting_power >= power_cap:
    print(f"Error: starting_power ({starting_power}) must be less than power_cap ({power_cap})")
    exit(1)

# Validate target_power
if target_power <= starting_power:
    print(f"Error: target_power ({target_power}) must be greater than starting_power ({starting_power})")
    exit(1)
if target_power > power_cap:
    print(f"Error: target_power ({target_power}) must be less than or equal to power_cap ({power_cap})")
    exit(1)

scenarios = {
    "Original (0 power bump at 400+)": [
        (450, 0, 2),  # At 400+: power_bump=0, prime_bump=3
        (400, 0, 3),  # At 400+: power_bump=0, prime_bump=3
        (297, 3, 4),  # At 297+: power_bump=3, prime_bump=4
        (196, 4, 5),  # At 196+: power_bump=4, prime_bump=5
        (0, 6, 7),  # Below 196: power_bump=6, prime_bump=7
    ],
    "Modified (+1 power bump at 400+)": [
        (450, 1, 2),  # At 400+: power_bump=0, prime_bump=3
        (400, 1, 3),  # At 400+: power_bump=1, prime_bump=3 (CHANGED)
        (297, 3, 4),  # At 297+: power_bump=3, prime_bump=4
        (196, 4, 5),  # At 196+: power_bump=4, prime_bump=5
        (0, 6, 7),  # Below 196: power_bump=6, prime_bump=7
    ],
}

# Run simulations for each scenario
results = []
for scenario_name, rules in scenarios.items():
    print(f"Running {N} simulations for: {scenario_name}")
    stats = run_scenario_analysis(
        N, scenario_name, power_cap, starting_power, target_power, prime_chance, rules
    )
    results.append(stats)
    print(f"  Completed - Mean activities: {stats['activity_mean']:.1f}\n")

# Display comparison results
print("=" * 60)
print(f"SCENARIO COMPARISON - {N} simulations each")
print(f"Target: {starting_power} → {target_power} power")
print(f"Prime chance: {prime_chance:.1%}")
print("=" * 60)

for stats in results:
    print(f"\n{stats['name']}:")
    print(f"  Activities to reach target_power ({target_power}):")
    print(f"    Mean: {stats['activity_mean']:.1f}")
    print(f"    Median: {stats['activity_median']:.1f}")
    print(f"    Std Dev: {stats['activity_stdev']:.1f}")
    print(f"    Range: {stats['activity_min']}-{stats['activity_max']}")
    print(
        f"    50% of runs: {stats['activity_25th']:.0f}-{stats['activity_75th']:.0f} activities"
    )
    print("  Prime drops:")
    print(f"    Mean: {stats['prime_mean']:.1f}")
    print(f"    Observed rate: {stats['prime_rate']:.4f}")

# Summary comparison
print("\n" + "=" * 60)
print("SUMMARY - Activities needed (mean):")
for stats in results:
    baseline = results[0]["activity_mean"]
    diff = stats["activity_mean"] - baseline
    pct_change = (diff / baseline) * 100
    if stats == results[0]:
        print(f"  {stats['name']}: {stats['activity_mean']:.1f} (baseline)")
    else:
        print(
            f"  {stats['name']}: {stats['activity_mean']:.1f} ({diff:+.1f}, {pct_change:+.1f}%)"
        )