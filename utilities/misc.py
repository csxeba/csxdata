"""Pure Python and Python stdlib based utilities are here.
This module aims to be PyPy compatible."""


def euclidean(itr, target):
    import math
    assert len(itr) == len(target), "Can't perform distance calculation"
    res = math.sqrt(sum([(itr[i]-target[i])**2 for i in range(len(itr))]))
    return res


def chooseN(iterable: list, n=1):
    """Choose n elements randomly from an iterable and remove the element"""
    return [choose(iterable) for _ in range(n)]  # TODO: untested. Is <iterable> modified in-place?


def choose(iterable: list):
    """Chooses an element randomly from a list, then removes it from the list"""
    import random
    out = random.randrange(len(iterable))
    return iterable.pop(out)  # TODO: untested. Is <iterable> modified in-place?


def feature_scale(iterable, from_=0, to=1):
    """Scales the elements of a vector between from_ and to uniformly"""
    # TODO: untested
    if max(iterable) + min(iterable) == 0:
        # print("Feature scale warning: every value is 0 in iterable!")
        return type(iterable)([from_ for _ in range(len(iterable))])

    out = []
    for e in iterable:
        try:
            x = ((e - min(iterable)) / (max(iterable) - min(iterable)) * (to - from_)) + from_
        except ZeroDivisionError:
            x = 0
        out.append(x)
    return type(iterable)(out)


def avg(iterable):
    return sum(iterable) / len(iterable)


def dehungarize(inflpath, outflpath=None, lower=False, decimal=False):
    dictionary = {"á": "a", "é": "e", "í": "i",
                  "ó": "o", "ö": "o", "ő": "o",
                  "ú": "u", "ü": "u", "ű": "u",
                  "Á": "A", "É": "E", "Í": "I",
                  "Ó": "O", "Ö": "O", "Ő": "O",
                  "Ú": "U", "Ü": "U", "Ű": "U"}
    with open(inflpath) as infl:
        txt = infl.read()
        infl.close()
    if lower:
        txt = txt.lower()
    for hunchar, asciichar in dictionary.items():
        txt = txt.replace(hunchar, asciichar)
    if decimal:
        txt = txt.replace(",", ".")
    if outflpath is None:
        return txt
    else:
        with open(outflpath, "w") as outfl:
            outfl.write(txt)
            outfl.close()


def niceround(number, places):
    if not isinstance(number, float):
        er = "Supplied parameter must be of type: float, not <{}>".format(type(number))
        if isinstance(number, str):
            if "." not in number:
                raise TypeError(er)
        else:
            raise TypeError(er)

    strnumber = str(number)
    if "." in strnumber:
        decpoint = strnumber.index(".")
    else:
        decpoint = len(strnumber)
    predec = strnumber[:decpoint]
    after = strnumber[decpoint+1:decpoint+places+1]
    return predec + "." + after


def padnumber(actual, maximum, pad=" ", before=True):
    strmax, stract = str(maximum), str(actual)
    maxlen, actlen = len(strmax), len(stract)

    if actlen > maxlen:
        raise ValueError("<actual> is bigger in string form than <maximum>!")

    pudding = pad * (maxlen - actlen)
    padact = (pudding + stract) if before else (stract + pudding)
    return padact


def ravel(a):
    """Recursive function to flatten a list of lists of lists..."""
    if not a:
        return a
    if isinstance(a[0], list):
        return ravel(a[0]) + ravel(a[1:])
    return a[:1] + ravel(a[1:])