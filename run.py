#!/usr/bin/env python
from sys import argv

import ties


if __name__ == "__main__":
    tie_name = argv[1]
    tie = getattr(ties, tie_name)()
    tie.prepare(*argv[2:])
    tie.run()
