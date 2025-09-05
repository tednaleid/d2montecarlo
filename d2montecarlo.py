#!/usr/bin/env -S uv run --script
import random

N = 1

power_cap = 450
starting_power = 400
prime_chance = 0.075

for i in range(N):
    activity_count = 0
    prime_count = 0
    gear = [starting_power for i in range(8)]
    account_power = sum(gear)//8

    while account_power < power_cap:
        activity_count += 1
        if account_power  >= 400:
            power_bump = 0
            prime_bump = 3
        elif account_power + 3 >= 300:
            power_bump = 3
            prime_bump = 4
        elif account_power + 4 >= 200:
            power_bump = 4
            prime_bump = 5
        else:
            power_bump = 6
            prime_bump = 7

        if random.random() <= prime_chance:
            prime_count += 1
            slot = random.randrange(8)
            gear[slot] = min(max(account_power + prime_bump, gear[slot]), power_cap)

        slot = random.randrange(8)
        gear[slot] = min(max(account_power + power_bump, gear[slot]), power_cap)

        # primes are rolled at the same time as the regular drop so we don't bump account power till after both drop
        account_power = sum(gear)//8

    print(f"activities: {activity_count} prime count: {prime_count} gear: {gear}")