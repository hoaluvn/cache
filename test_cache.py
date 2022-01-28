import sys
import yaml
import logging
import random
from memory import memory
from cache import cache
import pytest

''' setup logger '''
log_handlers = [logging.StreamHandler()]
logging.basicConfig(level=logging.INFO, handlers=log_handlers)

##########################################################
#### TEST start 
##########################################################
def test_read_after_write():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    raddr = int(random.random()* (2 ** 14)) * 4
    rdata = int(random.random() * (2 ** 32))
    cache1.cache_write(raddr, rdata)
    assert rdata == cache1.cache_read(raddr)

def test_no_write_through():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    cache2 = cache(mem=my_mem)
    raddr = int(random.random()* (2 ** 14)) * 4
    rdata = int(random.random() * (2 ** 32))
    cache1.cache_write(raddr, rdata)
    assert rdata != cache2.cache_read(raddr)

def test_write_back():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    cache2 = cache(mem=my_mem)
    raddr = int(random.random()* (2 ** 14)) * 4
    rdata = int(random.random() * (2 ** 32))
    cache1.cache_write(raddr, rdata)
    # Clean entry
    cache1.write_reg(1, raddr)
    cache1.write_reg(2, 4)
    cache1.write_reg(0, 2)
    assert rdata == cache2.cache_read(raddr)

def test_entry_replace():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    cache2 = cache(mem=my_mem)
    raddr = int(random.random()* (2 ** 14)) * 4
    rdata = int(random.random() * (2 ** 32))
    cache1.cache_write(raddr, rdata)
    cache1.cache_read(raddr + 8*4)
    assert rdata == cache2.cache_read(raddr)

def test_entry_invalidate():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    cache2 = cache(mem=my_mem)
    raddr = int(random.random()* (2 ** 14)) * 4
    rdata = int(random.random() * (2 ** 32))
    # first write
    cache1.cache_write(raddr, rdata)
    assert rdata == cache1.cache_read(raddr)
    # clean entry
    cache1.write_reg(1, raddr)
    cache1.write_reg(2, 4)
    cache1.write_reg(0, 2)
    # second write
    rdata2 = int(random.random() * (2 ** 32))
    cache1.cache_write(raddr, rdata2)
    assert rdata2 == cache1.cache_read(raddr)
    # invalidate
    cache1.write_reg(1, raddr)
    cache1.write_reg(2, 4)
    cache1.write_reg(0, 1)
    # read the first write
    assert rdata == cache1.cache_read(raddr)

def test_fillup():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    cache2 = cache(mem=my_mem)
    table = {}
    baddr = int(random.random()* (2 ** 14)) * 4
    # Fill up cache array
    for i in range(8):
        raddr = baddr + i*4 + i * 32 * random.randint(1,32)
        rdata = int(random.random() * (2 ** 32))
        table[raddr] = rdata
        cache1.cache_write(raddr, rdata)
    # Clean entry from baddr => +32*8
    cache1.write_reg(1, baddr)
    cache1.write_reg(2, 32*8)
    cache1.write_reg(0, 2)
    # Read back and check
    for addr in table:
        data = table[addr]
        if baddr <= addr <= baddr + 32*8:
            assert data == cache2.cache_read(addr)
        else:
            assert data != cache2.cache_read(addr)
