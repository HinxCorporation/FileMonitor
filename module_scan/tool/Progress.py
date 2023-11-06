from tqdm import tqdm


class Progress:
    """
    进度条类（就是对tqmd包了一层壳）
    """
    def __init__(self, total, desc, unit, unit_divisor, unit_scale):
        self.tqdm = tqdm(
            total=total,
            desc=desc,
            unit=unit,
            unit_divisor=unit_divisor,
            unit_scale=unit_scale
        )

    def update(self, count):
        self.tqdm.update(count)

    def close(self):
        self.tqdm.close()
