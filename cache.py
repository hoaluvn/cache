import logging

class cacherow:
    def __init__(self, index, addrw, tagw, indexw, dataw, mem=None):
        self.idx = index
        self.aw = addrw
        self.tw = tagw
        self.iw = indexw
        self.dw = dataw
        self.dirty = False
        self.valid = False
        self.tag   = 0
        self.data  = 0
        self.mem = mem
        self.addrmask = (2 ** addrw - 1) & ~(2 ** (addrw - tagw - indexw) - 1)

    def __get_tag(self, addr):
        _tag = addr >> (self.aw - self.tw)
        logging.debug("addr: 0x%x => tag: 0x%x", addr, _tag)
        return _tag

    def __get_addr(self, tag):
        a = self.tag << (self.aw - self.tw) 
        b = self.idx << (self.aw - self.tw - self.iw)
        _addr = a + b
        logging.debug("tag: 0x%x => addr: 0x%x", tag, _addr)
        return _addr

    def get_addr(self):
        if self.valid:
            return self.__get_addr(self.tag)

    def invalid_entry(self):
        self.valid = False
        self.dirty = False
        logging.info("Cache invalidate entry: %d", self.idx)

    def clean_entry(self):
        if self.valid and self.dirty:
            _addr = self.__get_addr(self.tag)
            self.mem.mem_write(_addr, self.data)
            self.dirty = False
            logging.info("Flush cache line to memory 0x%x => [0x%x]", self.data, _addr)

    def store(self, addr, data):
        tag   = self.__get_tag(addr)
        if self.valid and self.dirty and self.tag != tag:
            self.clean_entry()
        self.tag   = tag
        self.dirty = True
        self.valid = True
        self.data  = data & (2 ** self.dw - 1)

    def load(self, addr):
        _tag = self.__get_tag(addr)
        if self.valid:
            if self.tag == _tag:
                return self.data
            elif self.dirty:
                _addr = self.__get_addr(self.tag)
                self.mem.mem_write(_addr, self.data)
        self.tag = _tag
        self.valid = True
        self.dirty = False
        self.data  = self.mem.mem_read(addr & self.addrmask)
        return self.data

class cache:
    def __init__(self, addrw=16, tagw=11, idxw=3, dataw=32, mem=None):
        self.aw = addrw
        self.tw = tagw
        self.iw = idxw
        self.dw = dataw
        self.sz = 2 ** idxw
        self.reg = [0,0,0]
        self.cachearray = {}
        for i in range(self.sz):
            self.cachearray[i] = cacherow(i, self.aw, self.tw, self.iw, self.dw, mem)

    def __get_index(self, addr):
        _index = (addr >> (self.aw - self.tw - self.iw)) & (2 ** self.iw - 1)
        logging.debug("index: %d", _index)
        return _index

    def cache_write(self, addr, data):
        logging.info("Cache write start: [0x%04x] <= 0x%x", addr, data)
        idx = self.__get_index(addr)
        self.cachearray[idx].store(addr, data)
        logging.info("Cache write end")

    def cache_read(self, addr):
        logging.info("Cache read start: [0x%04x]", addr)
        idx = self.__get_index(addr)
        _data = self.cachearray[idx].load(addr)
        logging.info("Cache read end  : [0x%04x] => 0x%x", addr, _data)
        return _data

    def write_reg(self, rid, data):
        self.reg[rid] = data & (2 ** self.aw - 1)
        logging.debug("Register write [%d] = 0x%x", rid, self.reg[rid])
        if rid == 0: # Execute command
            cmd = data & 3
            if cmd == 0:
                return
            start_addr = self.reg[1]
            end_addr   = start_addr + self.reg[2]
            logging.debug("Test start_addr: 0x%x", start_addr)
            logging.debug("Test end_addr: 0x%x", end_addr)
            for i in range(self.sz):
                entry_addr = self.cachearray[i].get_addr()
                if self.cachearray[i].valid:
                    logging.debug("Checking entry address: entry[%d]:addr=0x%x", i, entry_addr)
                    if start_addr <= entry_addr <= end_addr:
                        if cmd == 3: # clean & invalidate
                            self.cachearray[i].clean_entry()
                            self.cachearray[i].invalid_entry()
                        elif cmd == 2: # clean entires
                            self.cachearray[i].clean_entry()
                        elif cmd == 1: # invalidate entries
                            self.cachearray[i].invalid_entry()
