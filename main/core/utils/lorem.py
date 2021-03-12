"""Generator for random text that looks like Latin."""
from django.utils import timezone
import random

__all__ = ['sentence', 'paragraph', 'text']

WORDS = ("adipisci aliquam amet consectetur dolor dolore dolorem eius est et"
         "incidunt ipsum labore magnam modi neque non numquam porro quaerat qui"
         "quia quisquam sed sit tempora ut velit voluptatem Lorem ipsum dolor"
         "sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt"
         "ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
         "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
         "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum"
         "dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat"
         "non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.").split()

class TextLorem():
    def __init__(self, wsep=' ', ssep=' ', psep='\n\n',
                 srange=(4, 8), prange=(5, 10), trange=(3, 6),
                 words=None):
        self._wsep = wsep
        self._ssep = ssep
        self._psep = psep
        self._srange = srange
        self._prange = prange
        self._trange = trange
        if words:
            self._words = words
        else:
            self._words = WORDS

    def sentence(self):
        n = random.randint(*self._srange)
        s = self._wsep.join(self._word() for _ in range(n))
        return s[0].upper() + s[1:] + '.'

    def paragraph(self):
        n = random.randint(*self._prange)
        p = self._ssep.join(self.sentence() for _ in range(n))
        return p

    def text(self):
        n = random.randint(*self._trange)
        t = self._psep.join(self.paragraph() for _ in range(n))
        return t

    def _word(self):
        return random.choice(self._words)

def sentence(*args, **kwargs):
    return TextLorem().sentence(*args, **kwargs)


def paragraph(*args, **kwargs):
    return TextLorem().paragraph(*args, **kwargs)


def text(*args, **kwargs):
    return TextLorem().text(*args, **kwargs)

def random_date(start=(timezone.now() - timezone.timedelta(days=10000)), end=timezone.now()):
    """
    This function will return a random datetime between two datetime
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = random.randrange(int_delta)
    return start + timezone.timedelta(seconds=random_second)
