import logging
import random
from memory import memory
from cache import cache

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

def test_random():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    cache2 = cache(mem=my_mem)
    table = {}
    baddr = int(random.random()* (2 ** 14)) * 4
    # Fill up cache array
    for i in range(8):
        raddr = baddr + i*4 + i * 32 * random.randint(1,32)
        raddr &= 2**16 - 1
        rdata = int(random.random() * (2 ** 32))
        table[raddr] = rdata
        cache1.cache_write(raddr, rdata)
    # Clean entry from saddr => eaddr 
    addrlist = list(table.keys())
    a = random.randrange(0, 7)
    b = random.randrange(0, 7)
    saddr = min(addrlist[a], addrlist[b])
    eaddr = max(addrlist[a], addrlist[b])
    cache1.write_reg(1, saddr)
    cache1.write_reg(2, eaddr - saddr)
    cache1.write_reg(0, 2)
    # Read back and check
    for addr in table:
        data = table[addr]
        if saddr <= addr <= eaddr:
            assert data == cache2.cache_read(addr)
        else:
            assert data != cache2.cache_read(addr)

def test_random_invalidate():
    my_mem = memory("database.yml")
    cache1 = cache(mem=my_mem)
    cache2 = cache(mem=my_mem)
    table = {}
    baddr = int(random.random()* (2 ** 14)) * 4
    # Fill up cache array
    for i in range(8):
        raddr = baddr + i*4 + i * 32 * random.randint(1,32)
        raddr &= 2**16 - 1
        rdata = int(random.random() * (2 ** 32))
        table[raddr] = rdata
        cache1.cache_write(raddr, rdata)
    # Invalidate entry from saddr => eaddr 
    addrlist = list(table.keys())
    a = random.randrange(0, 7)
    b = random.randrange(0, 7)
    saddr = min(addrlist[a], addrlist[b])
    eaddr = max(addrlist[a], addrlist[b])
    cache1.write_reg(1, saddr)
    cache1.write_reg(2, eaddr - saddr)
    cache1.write_reg(0, 1)
    # Clean entire cache mem
    cache1.write_reg(1, 0)
    cache1.write_reg(2, 2**16 -1)
    cache1.write_reg(0, 2)
    # Read back and check
    for addr in table:
        data = table[addr]
        if saddr <= addr <= eaddr:
            assert data != cache2.cache_read(addr)
        else:
            assert data == cache2.cache_read(addr)
