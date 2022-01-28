import sys
import yaml
import logging
import random
from memory import memory
from cache import cache

def usage():
    ''' TestCache '''

    print('''    aregr
    Usage: testcache [options]
    options:
    --seed  <SEED_NUMBER> :   Override project default configuration  file
    -l      <logfile>     :   Dump into <logfile>
    -d      <level>       :   Dump level: info(default), warning, debug
    -h,--help             :   Prints this message
    ''')


class Values:
    ''' Storage class '''
    def __init__(self, defaults=None):
        if defaults:
            for (attr, val) in list(defaults.items()):
                setattr(self, attr, val)

def get_logging_level(level):
    """ string to logging.Level """
    selector = logging.WARNING
    switcher = {"info"   : logging.INFO,
                "warning": logging.WARNING,
                "debug"  : logging.DEBUG
               }
    if level in switcher:
        selector = switcher[level]
    return selector

def parse_options():
    """ Parse command line args """
    m_args = sys.argv[1:]
    m_options = Values({
        "seed": None,
        "has_logfile" : None,
        "logfile" : "log",
        "loglevel": "info",
    })
    while m_args:
        if m_args[0] == '--seed':
            m_options.seed = m_args[1]
            m_args = m_args[2:]
        elif m_args[0] == '-l':
            m_options.has_logfile = 1
            m_options.logfile = m_args[1]
            m_args = m_args[2:]
        elif m_args[0] == '-d':
            m_options.loglevel = m_args[1]
            m_args = m_args[2:]
        elif m_args[0] in ('-h', '--help'):
            usage()
            sys.exit(0)
        elif m_args[0][0] == "-":
            print("Unknown option", m_args[0], file=sys.stderr)
            print(usage, file=sys.stderr)
            exit(0)
        else:
            break
    return (m_options, m_args)

if __name__ == '__main__':
    (options, args) = parse_options()

    ''' setup logger '''
    log_handlers = []
    log_handlers += [logging.StreamHandler()]
    if options.has_logfile:
        log_handlers += logging.FileHandler(filename=options.has_logfile, mode='a')
    logging.basicConfig(level=get_logging_level(options.loglevel), handlers=log_handlers)

    ''' setup randomization '''
    seed = random.randrange(sys.maxsize)
    if options.seed:
       seed = int(options.seed)
    logging.info("Seed was: %d", seed)
    random.seed(seed)

    my_mem = memory("database.yml")
    cc1 = cache(mem=my_mem)

    cc2 = cache(mem=my_mem)

#    tmp = cc1.cache_read(0)
#    cc.cache_write(32, tmp*2)
#
#    tmp = cc1.cache_read(0)
#    tmp = cc1.cache_read(100)

#    raddr = int(random.random()* (2 ** 14)) * 4
#    tmp = cc1.cache_read(raddr)


    cc.write_reg(0, 3)

#    cc.cache_flush()

    del cc
    del my_mem

def test_write_read():
    raddr = int(random.random()* (2 ** 14)) * 4
    rdata = int(random.random() * (2 ** 32))
    cc1.cache_write(raddr, rdata)
    assert rdata == cc1.cache_read(raddr)
