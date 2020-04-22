#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define uint32 uint32_t
#define uint64 uint64_t
#define int32 int32_t
#define int64 int64_t
#define randbool() get_randbool(&turnips.rng)
#define randint(a, b) get_randint(&turnips.rng, a, b)
#define randfloat(a, b) get_randfloat(&turnips.rng, a, b)
#define min(x, y) (((x) < (y)) ? (x) : (y))
#define DEBUG false

typedef struct _Random {
    uint32 m_context[4];
} Random;

uint32 get_u32(Random *random) {
    uint32 n = random->m_context[0] ^ (random->m_context[0] << 11);
    random->m_context[0] = random->m_context[1];
    random->m_context[1] = random->m_context[2];
    random->m_context[2] = random->m_context[3];
    random->m_context[3] =
        n ^ (n >> 8) ^ random->m_context[2] ^ (random->m_context[2] >> 19);
    return random->m_context[3];
}

uint64 get_u64(Random *random) {
    uint32 n1 = random->m_context[0] ^ (random->m_context[0] << 11);
    uint32 n2 = random->m_context[1];
    uint32 n3 = n1 ^ (n1 >> 8) ^ random->m_context[3];

    random->m_context[0] = random->m_context[2];
    random->m_context[1] = random->m_context[3];
    random->m_context[2] = n3 ^ (random->m_context[3] >> 19);
    random->m_context[3] =
        n2 ^ (n2 << 11) ^ ((n2 ^ (n2 << 11)) >> 8) ^ random->m_context[2] ^ (n3 >> 19);

    return (((uint64) random->m_context[2]) << 32) | random->m_context[3];
}
bool get_randbool(Random *random) {
    return get_u32(random) & 0x80000000;
}
int get_randint(Random *random, int min, int max) {
    return ((((uint64) get_u32(random)) * (uint64)(max - min + 1)) >> 32) + min;
}
float get_randfloat(Random *random, float a, float b) {
    uint32 val = 0x3f800000 | (get_u32(random) >> 9);
    float fval = *(float *) (&val);
    return a + ((fval - 1.0f) * (b - a));
}
int intceil(float val) {
    return (int) (val + 0.99999f);
}

typedef struct _TurnipPrices {
    int32 base_price;
    int32 sell_prices[14];
    uint32 what_pattern;
    int32 tmp40;
    Random rng;
    bool pattern_fits;
} TurnipPrices;

TurnipPrices calculate(TurnipPrices turnips, int base_price, int prices[]) {
    turnips.base_price = randint(90, 110);
    if (turnips.base_price != base_price) {
        turnips.pattern_fits = false;
        return turnips;
    }
    int chance = randint(0, 99);

    int next_pattern;

    if (turnips.what_pattern >= 4) {
        next_pattern = 2;
    } else {
        switch (turnips.what_pattern) {
        case 0:
            if (chance < 20) {
                next_pattern = 0;
            } else if (chance < 50) {
                next_pattern = 1;
            } else if (chance < 65) {
                next_pattern = 2;
            } else {
                next_pattern = 3;
            }
            break;
        case 1:
            if (chance < 50) {
                next_pattern = 0;
            } else if (chance < 55) {
                next_pattern = 1;
            } else if (chance < 75) {
                next_pattern = 2;
            } else {
                next_pattern = 3;
            }
            break;
        case 2:
            if (chance < 25) {
                next_pattern = 0;
            } else if (chance < 70) {
                next_pattern = 1;
            } else if (chance < 75) {
                next_pattern = 2;
            } else {
                next_pattern = 3;
            }
            break;
        case 3:
            if (chance < 45) {
                next_pattern = 0;
            } else if (chance < 70) {
                next_pattern = 1;
            } else if (chance < 85) {
                next_pattern = 2;
            } else {
                next_pattern = 3;
            }
            break;
        }
    }
    turnips.what_pattern = next_pattern;

    for (int i = 2; i < 14; i++) {
        turnips.sell_prices[i] = 0;
    }
    turnips.sell_prices[0] = turnips.base_price;
    turnips.sell_prices[1] = turnips.base_price;

    int work;
    int dec_1, dec_2, peak_start;
    int hi_1, hi_2, hi_3;
    float rate;

    switch (next_pattern) {
    case 0:
        work = 2;
        dec_1 = randbool() ? 3 : 2;
        dec_2 = 5 - dec_1;

        hi_1 = randint(0, 6);
        hi_2 = 7 - hi_1;
        hi_3 = randint(0, hi_2 - 1);

        for (int i = 0; i < hi_1; i++) {
            turnips.sell_prices[work] =
                intceil(randfloat(0.9, 1.4) * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            work++;
        }

        rate = randfloat(.8, .6);
        for (int i = 0; i < dec_1; i++) {
            turnips.sell_prices[work] = intceil(rate * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            work++;
            rate -= 0.04;
            rate -= randfloat(0, .06);
        }

        for (int i = 0; i < hi_2 - hi_3; i++) {
            turnips.sell_prices[work] =
                intceil(randfloat(.9, 1.4) * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            work++;
        }

        rate = randfloat(0.8, 0.6);
        for (int i = 0; i < dec_2; i++) {
            turnips.sell_prices[work] = intceil(rate * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            work++;
            rate -= 0.04;
            rate -= randfloat(0, 0.06);
        }

        // high phase 3
        for (int i = 0; i < hi_3; i++) {
            turnips.sell_prices[work] =
                intceil(randfloat(0.9, 1.4) * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            work++;
        }
        break;
    case 1:
        // PATTERN 1: decreasing middle, high spike, random low
        peak_start = randint(3, 9);
        rate = randfloat(0.9, 0.85);
        for (work = 2; work < peak_start; work++) {
            turnips.sell_prices[work] = intceil(rate * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            rate -= 0.03;
            rate -= randfloat(0, 0.02);
        }
        turnips.sell_prices[work] = intceil(randfloat(0.9, 1.4) * turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        turnips.sell_prices[work] = intceil(randfloat(1.4, 2.0) * turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        turnips.sell_prices[work] = intceil(randfloat(2.0, 6.0) * turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        turnips.sell_prices[work] = intceil(randfloat(1.4, 2.0) * turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        turnips.sell_prices[work] = intceil(randfloat(0.9, 1.4) * turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        for (; work < 14; work++) {
            turnips.sell_prices[work] =
                intceil(randfloat(0.4, 0.9) * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
        }
        break;
    case 2:
        // PATTERN 2: consistently decreasing
        rate = 0.9;
        rate -= randfloat(0, 0.05);
        for (work = 2; work < 14; work++) {
            turnips.sell_prices[work] = intceil(rate * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            rate -= 0.03;
            rate -= randfloat(0, 0.02);
        }
        break;
    case 3:
        // PATTERN 3: decreasing, spike, decreasing
        peak_start = randint(2, 9);

        // decreasing phase before the peak
        rate = randfloat(0.9, 0.4);
        for (work = 2; work < peak_start; work++) {
            turnips.sell_prices[work] = intceil(rate * turnips.base_price);
            if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                turnips.pattern_fits = false;
                return turnips;
            }
            rate -= 0.03;
            rate -= randfloat(0, 0.02);
        }

        turnips.sell_prices[work] =
            intceil(randfloat(0.9, 1.4) * (float) turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        turnips.sell_prices[work] = intceil(randfloat(0.9, 1.4) * turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        rate = randfloat(1.4, 2.0);
        turnips.sell_prices[work] =
            intceil(randfloat(1.4, rate) * turnips.base_price) - 1;
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        turnips.sell_prices[work] = intceil(rate * turnips.base_price);
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;
        turnips.sell_prices[work] =
            intceil(randfloat(1.4, rate) * turnips.base_price) - 1;
        if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
            turnips.pattern_fits = false;
            return turnips;
        }
        work++;

        // decreasing phase after the peak
        if (work < 14) {
            rate = randfloat(0.9, 0.4);
            for (; work < 14; work++) {
                turnips.sell_prices[work] = intceil(rate * turnips.base_price);
                if (prices[work] != -1 && prices[work] != turnips.sell_prices[work]) {
                    turnips.pattern_fits = false;
                    return turnips;
                }
                rate -= 0.03;
                rate -= randfloat(0, 0.02);
            }
        }
        break;
    }

    turnips.sell_prices[0] = 0;
    turnips.sell_prices[1] = 0;
    turnips.pattern_fits = true;
    return turnips;
}

void print_prog(uint64 seed, uint64 pattern) {
    fprintf(stderr, "Complete: %11lu / %lu (%3lu%%)\r", seed * 4 + pattern,
            (uint64) UINT32_MAX * 4,
            ((seed * 4 + pattern) * 100) / ((uint64) UINT32_MAX * 4));
}

int main(int argc, char **argv) {
    if (argc == 1) {
        puts("Pass buy price, then sale prices. -1 to mark unknown");
        return 1;
    }
    int sell_prices[14];
    int buy_price = atoi(argv[1]);
    int arg;
    for (arg = 2; arg < argc; arg++) {
        sell_prices[arg] = atoi(argv[arg]);
    }
    for (; arg < 14; arg++) {
        sell_prices[arg] = -1;
    }
    TurnipPrices turnips;
    Random random;
    if (DEBUG) {
        turnips.rng = random;
        turnips.rng.m_context[0] = 0x6C078965u * (1234u ^ (1234u >> 30)) + 1;
        turnips.rng.m_context[1] = 0x6C078965u * (turnips.rng.m_context[0] ^
                                                  (turnips.rng.m_context[0] >> 30)) +
                                   2;
        turnips.rng.m_context[2] = 0x6C078965u * (turnips.rng.m_context[1] ^
                                                  (turnips.rng.m_context[1] >> 30)) +
                                   3;
        turnips.rng.m_context[3] = 0x6C078965u * (turnips.rng.m_context[2] ^
                                                  (turnips.rng.m_context[2] >> 30)) +
                                   4;
        turnips.what_pattern = 1;
        turnips = calculate(turnips, buy_price, sell_prices);
        fprintf(stderr, "Pattern %u\nPrices", 1);
        for (int i = 0; i < 14; i++) {
            fprintf(stderr, " %u", turnips.sell_prices[i]);
        }
        fprintf(stderr, "\nBuy price %u\n", turnips.base_price);
        return 0;
    }
    uint32 m_context[4];
    uint64 next_print = 1000;
    uint32 seed_1 = 0, seed_2 = 0, seed_3 = 0, seed_4 = 0;
    do {
        do {
            do {
                do {
                    m_context[0] = seed_1;
                    m_context[1] = seed_2;
                    m_context[2] = seed_3;
                    m_context[3] = seed_4;
                    memcpy(turnips.rng.m_context, m_context, sizeof m_context);
                    if (randint(90, 110) != buy_price) {
                        // if ((uint64) seed * 4 > next_print) {
                        //     print_prog(seed, 0);
                        //     next_print += 1000;
                        // }
                        // seed++;
                        continue;
                    }
                    for (int pattern = 0; pattern < 4; pattern++) {
                        memcpy(turnips.rng.m_context, m_context, sizeof m_context);
                        turnips.what_pattern = pattern;
                        turnips = calculate(turnips, buy_price, sell_prices);
                        if (!turnips.pattern_fits) {
                            continue;
                        }
                        // for (int i = 2; i < min(argc, 14); i++) {
                        //     if (sell_prices[i] == -1) {
                        //         continue;
                        //     }
                        //     if (sell_prices[i] != turnips.sell_prices[i]) {
                        //         goto skip_print;
                        //     }
                        // }
                        printf("%u %u %u %u %u %u %u %u %u %u\n", m_context[0],
                               m_context[1], m_context[2], m_context[3], pattern,
                               turnips.rng.m_context[0], turnips.rng.m_context[1],
                               turnips.rng.m_context[2], turnips.rng.m_context[3],
                               turnips.what_pattern);

                        // skip_print:
                        //     if ((uint64) seed * 4 + (uint64) pattern + 1 >
                        //     next_print) {
                        //         print_prog(seed, pattern);
                        //         next_print += 1000;
                        //     }
                        // }
                        seed_4++;
                    }
                } while (seed_4 != 0);
                seed_3++;
            } while (seed_3 != 0);
            seed_2++;
        } while (seed_2 != 0);
        seed_1++;
    } while (seed_1 != 0);
}
