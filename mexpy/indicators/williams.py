class Williams(object):

    @staticmethod
    def down_fractal(lows: list) -> list:
        def _fractal(low, n):
            if n + 3 > len(lows):
                return None

            low1 = ((lows[n - 2] > lows[n]) and (lows[n - 1] > lows[n]) and (lows[n + 1] > lows[n]) and (
                        lows[n + 2] > lows[n]))
            low2 = ((lows[n - 3] > lows[n]) and (lows[n - 2] > lows[n]) and (lows[n - 1] == lows[n]) and (
                        lows[n + 1] > lows[n]) and (lows[n + 2] > lows[n]))
            low3 = ((lows[n - 4] > lows[n]) and (lows[n - 3] > lows[n]) and (lows[n - 2] == lows[n]) and (
                        lows[n - 1] >= lows[n]) and (lows[n + 1] > lows[n]) and (lows[n + 2] > lows[n]))
            low4 = ((lows[n - 5] > lows[n]) and (lows[n - 4] > lows[n]) and (lows[n - 3] == lows[n]) and (
                        lows[n - 2] == lows[n]) and (lows[n - 1] >= lows[n]) and (lows[n + 1] > lows[n]) and (
                                lows[n + 2] > lows[n]))
            low5 = ((lows[n - 6] > lows[n]) and (lows[n - 5] > lows[n]) and (lows[n - 4] == lows[n]) and (
                        lows[n - 3] >= lows[n]) and (lows[n - 2] == lows[n]) and (lows[n - 1] >= lows[n]) and (
                                lows[n + 1] > lows[n]) and (lows[n + 2] > lows[n]))

            if low1 or low2 or low3 or low4 or low5:
                return low

            return None

        fractals = [_fractal(x, i) for i, x in enumerate(lows)]

        return fractals

    @staticmethod
    def up_fractal(highs: list) -> list:
        def _fractal(high, n):
            if n + 3 > len(highs):
                return None

            up1 = ((highs[n - 2] < highs[n]) and (highs[n - 1] < highs[n]) and (highs[n + 1] < highs[n]) and (
                        highs[n + 2] < highs[n]))
            up2 = ((highs[n - 3] < highs[n]) and (highs[n - 2] < highs[n]) and (highs[n - 1] == highs[n]) and (
                        highs[n + 1] < highs[n]) and (highs[n + 2] < highs[n]))
            up3 = ((highs[n - 4] < highs[n]) and (highs[n - 3] < highs[n]) and (highs[n - 2] == highs[n]) and (
                        highs[n - 1] <= highs[n]) and (highs[n + 1] < highs[n]) and (highs[n + 2] < highs[n]))
            up4 = ((highs[n - 5] < highs[n]) and (highs[n - 4] < highs[n]) and (highs[n - 3] == highs[n]) and (
                        highs[n - 2] == highs[n]) and (highs[n - 1] <= highs[n]) and (highs[n + 1] < highs[n]) and (
                               highs[n + 2] < highs[n]))
            up5 = ((highs[n - 6] < highs[n]) and (highs[n - 5] < highs[n]) and (highs[n - 4] == highs[n]) and (
                        highs[n - 3] <= highs[n]) and (highs[n - 2] == highs[n]) and (highs[n - 1] <= highs[n]) and (
                               highs[n + 1] < highs[n]) and (highs[n + 2] < highs[n]))

            if up1 or up2 or up3 or up4 or up5:
                return high

            return None

        fractals = [_fractal(x, i) for i, x in enumerate(highs)]

        return fractals
