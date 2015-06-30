import os
import sys


if hasattr(sys, 'real_prefix'):
    print 'VIRTUALENV'
else:
    print 'NORMAL PYTHON'

if __package__ == '':
    path = os.path.dirname(os.path.dirname(__file__))
    print 'setting path to ', path
    sys.path.insert(0, path)


import blacknight


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'util':
        sys.argv.pop(1)
        blacknight.util()
    if len(sys.argv) > 1 and sys.argv[1] == 'euca':
        sys.argv.pop(1)
        blacknight.euca()
    else:
        blacknight.main()
