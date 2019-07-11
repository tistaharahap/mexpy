def vwma(closes: list, volumes: list, period: int) -> list:
    def _vwma(n):
        if n < period:
            return closes[n]

        first_index = n - period
        closes_with_period = closes[first_index:n]
        vols_with_period = volumes[first_index:n]

        closes_with_period = [closes_with_period[i] * vols_with_period[i] for i, x in enumerate(closes_with_period)]

        res = sum(closes_with_period) / sum(vols_with_period)

        return res

    result = [_vwma(i) for i, x in enumerate(closes)]

    return result
