class human_format:
    """
    Human formatter

    Parameters
    ----------

    Examples
    --------
    >>> x = [1000, 1000000, 20000000]
    >>> human_format()(x)
    ['1K', '1M', '20M']
    """
    def __init__(self):
        pass

    def __format_single(self, single_num):
        num = float('{:.3g}'.format(single_num))
        magnitude = 0
        magnitude = (len(str(int(num)))-1)//3
        num /= 10 ** (3 * magnitude)
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    def __call__(self, x):
        if len(x) == 0:
            return []

        # format and then remove superfluous zeros
        labels = [self.__format_single(num) for num in x]
        return labels