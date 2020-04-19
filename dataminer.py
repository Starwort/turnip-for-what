#!/usr/bin/python3
import struct
from concurrent.futures import ProcessPoolExecutor
from sys import stdout
from typing import Any, Iterable, List, Optional, TextIO, Tuple, Union, cast

import click

# algorithms from https://gist.github.com/Treeki/85be14d297c80c8b3c0a76375743325b

MContext = Tuple[int, int, int, int]


class Random:
    m_context: MContext

    def __init__(
        self,
        seed: int = None,
        seed_2: int = None,
        seed_3: int = None,
        seed_4: int = None,
    ) -> None:
        if seed is None:
            seed = 42069  # wait I probably didn't need this lol
        if seed_2 is None:
            m_context = []
            m_context.append((0x6C078965 * (seed ^ (seed >> 30)) + 1) % (2 ** 32))
            for i in range(3):
                m_context.append(
                    (0x6C078965 * (m_context[i] ^ (m_context[i] >> 30)) + i + 2)
                    % (2 ** 32)
                )
            self.m_context = cast(MContext, tuple(m_context))
        else:
            seed_2 = cast(int, seed_2)
            seed_3 = cast(int, seed_3)
            seed_4 = cast(int, seed_4)
            if not (seed | seed_2 | seed_3 | seed_4):
                seed = 1
                seed_2 = 0x6C078967
                seed_3 = 0x714ACB41
                seed_4 = 0x48077044
            self.m_context = (
                seed % (2 ** 32),
                seed_2 % (2 ** 32),
                seed_3 % (2 ** 32),
                seed_4 % (2 ** 32),
            )

    def get_u32(self) -> int:
        n = (self.m_context[0] ^ (self.m_context[0] << 11)) % (2 ** 32)

        m_context = list(self.m_context)
        m_context.pop(0)
        m_context.append(
            (n ^ (n >> 8) ^ m_context[2] ^ (m_context[2] >> 19)) % (2 ** 32)
        )
        self.m_context = cast(MContext, tuple(m_context))

        return self.m_context[3]

    def get_u64(self) -> int:
        n1 = self.m_context[0] ^ (self.m_context[0] << 11)
        n2 = self.m_context[1]
        n3 = n1 ^ (n1 >> 8) ^ self.m_context[3]

        m_context = list(self.m_context)
        m_context.pop(0)
        m_context.pop(0)
        m_context.append((n3 ^ (m_context[1] >> 19)) % (2 ** 32))
        m_context.append(
            (n2 ^ (n2 << 11) ^ ((n2 ^ (n2 << 11)) >> 8) ^ m_context[0] ^ (n3 >> 19))
            % (2 ** 32)
        )
        self.m_context = cast(MContext, tuple(m_context))

        return (self.m_context[2] << 32) | self.m_context[3]

    def randint(self, min: int, max: int) -> int:
        return (((self.get_u32() * (max - min + 1)) >> 32) + min) % (2 ** 32)

    def get_context(self) -> MContext:
        return self.m_context


class TurnipPrices:
    base_price: int
    sell_prices: List[int]
    what_pattern: int
    rng: Random

    def __init__(self, what_pattern: int, *seeds: int) -> None:
        self.base_price = -1
        self.sell_prices = [0 for i in range(14)]
        self.what_pattern = what_pattern
        self.rng = Random(*seeds)

    def randbool(self) -> bool:
        return bool(self.rng.get_u32() & 0x80000000)

    def randint(self, min: int, max: int) -> int:
        return (((self.rng.get_u32() * (max - min + 1)) >> 32) + min) % (2 ** 32)

    def randfloat(self, a: float, b: float) -> float:
        val = (0x3F800000 | (self.rng.get_u32() >> 9)) % (2 ** 32)
        fval = struct.unpack("<f", val.to_bytes(4, "little"))[0]
        return a + ((fval - 1) * (b - a))

    def intceil(self, val: float) -> int:
        return int(val + 0.99999)

    def calculate(self):
        self.base_price = self.randint(90, 110)
        chance = self.randint(0, 99)
        # print(self.base_price, chance, self.what_pattern)

        next_pattern: int

        if self.what_pattern >= 4:
            next_pattern = 2
        else:
            if self.what_pattern == 0:
                if chance < 20:
                    next_pattern = 0
                elif chance < 50:
                    next_pattern = 1
                elif chance < 65:
                    next_pattern = 2
                else:
                    next_pattern = 3
            elif self.what_pattern == 1:
                if chance < 50:
                    next_pattern = 0
                elif chance < 55:
                    next_pattern = 1
                elif chance < 75:
                    next_pattern = 2
                else:
                    next_pattern = 3
            elif self.what_pattern == 2:
                if chance < 25:
                    next_pattern = 0
                elif chance < 70:
                    next_pattern = 1
                elif chance < 75:
                    next_pattern = 2
                else:
                    next_pattern = 3
            elif self.what_pattern == 3:
                if chance < 45:
                    next_pattern = 0
                elif chance < 70:
                    next_pattern = 1
                elif chance < 85:
                    next_pattern = 2
                else:
                    next_pattern = 3

        self.what_pattern = next_pattern

        for i in range(2, 14):
            self.sell_prices[i] = 0
        self.sell_prices[0] = self.base_price
        self.sell_prices[1] = self.base_price

        work: int
        dec_phase_len_1: int
        dec_phase_len_2: int
        peak_start: int
        high_phase_len_1: int
        high_phase_len_2_and_3: int
        high_phase_len_3: int
        rate: float
        if self.what_pattern == 0:
            work = 2
            dec_phase_len_1 = 3 if self.randbool() else 2
            dec_phase_len_2 = 5 - dec_phase_len_1

            high_phase_len_1 = self.randint(0, 6)
            high_phase_len_2_and_3 = 7 - high_phase_len_1
            high_phase_len_3 = self.randint(0, high_phase_len_2_and_3 - 1)

            for i in range(high_phase_len_1):
                self.sell_prices[work] = self.intceil(
                    self.randfloat(0.9, 1.4) * self.base_price
                )
                work += 1

            rate = self.randfloat(0.8, 0.6)
            for i in range(dec_phase_len_1):
                self.sell_prices[work] = self.intceil(rate * self.base_price)
                work += 1
                rate -= 0.04
                rate -= self.randfloat(0, 0.06)

            for i in range(high_phase_len_2_and_3 - high_phase_len_3):
                self.sell_prices[work] = self.intceil(
                    self.randfloat(0.9, 1.4) * self.base_price
                )
                work += 1

            rate = self.randfloat(0.8, 0.6)
            for i in range(dec_phase_len_2):
                self.sell_prices[work] = self.intceil(rate * self.base_price)
                work += 1
                rate -= 0.04
                rate -= self.randfloat(0, 0.06)

            for i in range(high_phase_len_3):
                self.sell_prices[work] = self.intceil(
                    self.randfloat(0.9, 1.4) * self.base_price
                )
        elif self.what_pattern == 1:
            peak_start = self.randint(3, 9)
            rate = self.randfloat(0.9, 0.85)
            for work in range(2, peak_start):
                self.sell_prices[work] = self.intceil(rate * self.base_price)
                rate -= 0.03
                rate -= self.randfloat(0, 0.02)
            work += 1
            self.sell_prices[work] = self.intceil(
                self.randfloat(0.9, 1.4) * self.base_price
            )
            work += 1
            self.sell_prices[work] = self.intceil(
                self.randfloat(1.4, 2.0) * self.base_price
            )
            work += 1
            self.sell_prices[work] = self.intceil(
                self.randfloat(2.0, 6.0) * self.base_price
            )
            work += 1
            self.sell_prices[work] = self.intceil(
                self.randfloat(1.4, 2.0) * self.base_price
            )
            work += 1
            self.sell_prices[work] = self.intceil(
                self.randfloat(0.9, 1.4) * self.base_price
            )
            work += 1
            for work in range(work, 14):
                self.sell_prices[work] = self.intceil(
                    self.randfloat(0.4, 0.9) * self.base_price
                )
        elif self.what_pattern == 2:
            rate = 0.9
            rate -= self.randfloat(0, 0.05)
            for work in range(2, 14):
                self.sell_prices[work] = self.intceil(rate * self.base_price)
                rate -= 0.03
                rate -= self.randfloat(0, 0.02)
        elif self.what_pattern == 3:
            peak_start = self.randint(2, 9)

            rate = self.randfloat(0.9, 0.4)
            for work in range(2, peak_start):
                self.sell_prices[work] = self.intceil(rate * self.base_price)
                rate -= 0.03
                rate -= self.randfloat(0, 0.02)
            work = peak_start

            self.sell_prices[work] = self.intceil(
                self.randfloat(0.9, 1.4) * self.base_price
            )
            work += 1
            self.sell_prices[work] = self.intceil(
                self.randfloat(0.9, 1.4) * self.base_price
            )
            work += 1
            rate = self.randfloat(1.4, 2.0)
            self.sell_prices[work] = (
                self.intceil(self.randfloat(1.4, rate) * self.base_price) - 1
            )
            work += 1
            self.sell_prices[work] = self.intceil(rate * self.base_price)
            work += 1
            self.sell_prices[work] = self.intceil(
                self.randfloat(1.4, rate) * self.base_price
            )
            work += 1

            if work < 14:
                rate = self.randfloat(0.9, 0.4)
                for work in range(work, 14):
                    self.sell_prices[work] = self.intceil(rate * self.base_price)
                    rate -= 0.03
                    rate -= self.randfloat(0, 0.02)
        self.sell_prices[0] = 0
        self.sell_prices[1] = 0


def main(pattern: int, *seeds: int):
    turnips = TurnipPrices(pattern, *seeds)
    turnips.calculate()
    print(
        (
            "Pattern {}:\n"
            "Sun Mon Tue Wed Thu Fri Sat\n"
            "{:>3} {:>3} {:>3} {:>3} {:>3} {:>3} {:>3}\n"
            "    {:>3} {:>3} {:>3} {:>3} {:>3} {:>3}\n"
            "New seeds: {} {} {} {}"
        ).format(
            turnips.what_pattern,
            turnips.base_price,
            *turnips.sell_prices[2:14:2],
            *turnips.sell_prices[3:15:2],
            *turnips.rng.get_context(),
        )
    )


def export(data: List[Tuple[MContext, int, MContext, int]], file: TextIO) -> None:
    file.write(
        "".join(
            "{} {} {} {} {} {} {} {} {} {}\n".format(
                *seeds, old_pattern, *context, pattern
            )
            for seeds, old_pattern, context, pattern in data
        )
    )


def import_(file: TextIO) -> List[Tuple[MContext, int, MContext, int]]:
    data: List[Tuple[MContext, int, MContext, int]] = []
    for line in file:
        values = list(map(int, line.split()))
        seeds = (values[0], values[1], values[2], values[3])
        old_pattern = values[4]
        context = (values[5], values[6], values[7], values[8])
        pattern = values[9]
        data.append((seeds, old_pattern, context, pattern))
    return data


def step_progbar(progbar: Any, step=1) -> None:
    if progbar is not None:
        try:
            progbar.update(step)  # click
        except AttributeError:
            progbar.step(step)  # ttk


def brute_force(
    buy_price: int,
    sell_prices: List[Optional[int]],
    portion: slice = slice(None),
    progbar: Any = None,
) -> List[Tuple[MContext, int, MContext, int]]:
    options: List[Tuple[MContext, int, MContext, int]] = []
    for seed in range(2 ** 32)[portion]:
        if not Random(seed).randint(90, 110) == buy_price:
            step_progbar(progbar, 4)
            continue
        for pattern in range(4):
            turnips = TurnipPrices(pattern, seed)
            turnips.calculate()
            for calculated, real in zip(turnips.sell_prices[2:], sell_prices):
                if real is None:
                    continue
                if calculated == real:
                    continue
                break
            else:
                options.append(
                    (
                        Random(seed).get_context(),
                        pattern,
                        turnips.rng.get_context(),
                        turnips.what_pattern,
                    )
                )
            step_progbar(progbar)
    return options


def brute_force_from_options(
    buy_price: int,
    sell_prices: List[Optional[int]],
    options: List[Tuple[MContext, int, MContext, int]],
    portion: slice = slice(None),
    progbar: Any = None,
) -> List[Tuple[MContext, int, MContext, int]]:
    new_options: List[Tuple[MContext, int, MContext, int]] = []
    _: Any
    for _, _, seeds, pattern in options[portion]:
        if not Random(*seeds).randint(90, 110) == buy_price:
            step_progbar(progbar)
            continue
        turnips = TurnipPrices(pattern, *seeds)
        turnips.calculate()
        for calculated, real in zip(turnips.sell_prices[2:], sell_prices):
            if real is None:
                continue
            if calculated == real:
                continue
            break
        else:
            new_options.append(
                (seeds, pattern, turnips.rng.get_context(), turnips.what_pattern)
            )
        step_progbar(progbar)
    return new_options


def narrow_down_options(
    buy_price: int,
    sell_prices: List[Optional[int]],
    options: List[Tuple[MContext, int, MContext, int]],
    portion: slice = slice(None),
    progbar: Any = None,
) -> List[Tuple[MContext, int, MContext, int]]:
    new_options: List[Tuple[MContext, int, MContext, int]] = []
    for seeds, pattern, _, _ in options[portion]:
        if not Random(*seeds).randint(90, 110) == buy_price:
            step_progbar(progbar)
            continue
        turnips = TurnipPrices(pattern, *seeds)
        turnips.calculate()
        for calculated, real in zip(turnips.sell_prices[2:], sell_prices):
            if real is None:
                continue
            if calculated == real:
                continue
            break
        else:
            new_options.append(
                (seeds, pattern, turnips.rng.get_context(), turnips.what_pattern)
            )
        step_progbar(progbar)
    return new_options


@click.group()
@click.help_option("--help", "-h")
@click.version_option("1.0.0", "--version", "-V", message="%(prog)s %(version)s")
def cli():
    pass


@cli.command()
@click.help_option("--help", "-h")
@click.argument("pattern", nargs=1, type=click.IntRange(0, 3))
@click.argument("seed", nargs=1, type=click.IntRange(0, 2 ** 32 - 1))
@click.option(
    "--seeds",
    nargs=3,
    type=click.IntRange(0, 2 ** 32 - 1),
    help="Island's other 3 random seeds",
)
def predict(pattern, seed, seeds):
    """Calculate turnip prices based on the previous pattern and island seed(s)
    
    \b
    PATTERN: Previous turnip pattern. Integer in [0, 3].
    SEED:    (First) island random seed. Any valid uint32.
    """
    if seeds:
        main(pattern, seed, *seeds)
    else:
        main(pattern, seed)


def get_chunks(
    data_len: int, process_count: int, process_ids: Union[Tuple[int, ...], range]
) -> List[slice]:
    chunk_len = data_len // process_count
    if process_ids == (-1,):
        process_ids = range(process_count)
    return [
        slice(
            chunk_len * process_id,
            (chunk_len * (process_id + 1))
            if process_id != process_count - 1
            else data_len,
        )
        for process_id in process_ids
    ]


def dispatch_file_brute_force(
    buy: int,
    sell: List[Optional[int]],
    in_: TextIO,
    out: TextIO,
    proc_count: int,
    proc_nos: Tuple[int, ...],
    this_week: bool,
):
    options = import_(in_)
    func = narrow_down_options if this_week else brute_force_from_options
    chunks = get_chunks(len(options), proc_count, proc_nos)
    if len(chunks) == 1:
        chunk = chunks[0]
        with click.progressbar(
            length=chunk.stop - chunk.start,
            label=(
                "Narrowing down options [{}-{}]"
                if this_week
                else "Generating options [{}-{}]"
            ).format(chunk.start, chunk.stop),
        ) as progbar:
            export(func(buy, sell, options, chunk, progbar), out)
    else:
        futures = []
        with click.progressbar(chunks, label="Submitting workers") as slice_bar:
            with ProcessPoolExecutor(max_workers=proc_count) as ppe:
                for chunk in slice_bar:
                    futures.append(ppe.submit(func, buy, sell, options, chunk))
        with click.progressbar(futures, label="Collecting results") as future_bar:
            for future in future_bar:
                export(future.result(), out)


def dispatch_no_file_brute_force(
    buy: int,
    sell: List[Optional[int]],
    out: TextIO,
    proc_count: int,
    proc_nos: Tuple[int, ...],
):
    chunks = get_chunks(2 ** 32, proc_count, proc_nos)
    if len(chunks) == 1:
        chunk = chunks[0]
        progbar: Iterable
        with click.progressbar(
            length=chunk.stop - chunk.start,
            label="Brute-forcing [{}-{}]".format(chunk.start, chunk.stop),
        ) as progbar:
            export(brute_force(buy, sell, chunk, progbar), out)
    else:
        futures = []
        with click.progressbar(chunks, label="Submitting workers") as slice_bar:
            with ProcessPoolExecutor(max_workers=proc_count) as ppe:
                for chunk in slice_bar:
                    futures.append(ppe.submit(brute_force, buy, sell, chunk))
        with click.progressbar(futures, label="Collecting results") as future_bar:
            for future in future_bar:
                export(future.result(), out)


@cli.command(name="brute-force")
@click.help_option("--help", "-h")
@click.argument("buy_price", type=click.IntRange(min=90, max=110), nargs=1)
@click.argument("sell_prices", type=int, nargs=-1)
@click.option("--input-file", "-i", type=click.File("r"), help="Previous output file")
@click.option(
    "--out-file",
    "-o",
    type=click.File("w"),
    default=stdout,
    help=(
        "File to which to write the resultant "
        "list of possible patterns. Defaults to stdout"
    ),
)
@click.option(
    "--processes",
    "-p",
    type=click.IntRange(min=1),
    default=1,
    help="How many processes to split the brute-forcing into.",
)
@click.option(
    "--process",
    "-P",
    type=click.IntRange(min=-1),
    default=(-1,),
    multiple=True,
    help=(
        "Which process(es) to act as for the brute-force. -1 (default) "
        "= run all processes. Most users won't need this setting, "
        "but it could be useful for running on multiple machines."
    ),
)
@click.option(
    "--check-current/--next",
    "--check/ ",
    "-c/-n",
    default=False,
    help=(
        "Whether to --check-current week, or to calculate prices for --next week. "
        "Can only be set if using an input file."
    ),
)
def cmd_brute_force(
    buy_price, sell_prices, input_file, out_file, processes, process, check_current
):
    """Brute-force your island random seeds based on the buy/sell prices of turnips.

    \b
    BUY_PRICE:   Price for which turnips were sold on Sunday
    SELL_PRICES: Prices for which turnips were saleable throughout the week, in the
                 morning and the afternoon of each day.
    """
    new_prices: Optional[int] = []
    for price in sell_prices:
        if price != -1:
            new_prices.append(price)
        else:
            new_prices.append(None)
    if input_file is not None:
        dispatch_file_brute_force(
            buy_price,
            new_prices,
            input_file,
            out_file,
            processes,
            process,
            check_current,
        )
    else:
        if check_current:
            print(
                "Cannot use --check-current without "
                "specifying the data to check against!"
            )
            exit(1)
        dispatch_no_file_brute_force(
            buy_price, new_prices, out_file, processes, process
        )


if __name__ == "__main__":
    cli()
