import yaml
import logging
from random import random

class memory:
    """
    Main memory model
       storage_path  : "secondary" storage
       addr_width    :
       byte_align    :
       data_width    :
    """
    def __init__(self, storage_path="db.yml", addr_width=16, byte_align=4, data_width=32):
        self.storage    = storage_path
        self.addr_width = int(addr_width)
        self.byte_align = int(byte_align)
        self.data_width = int(data_width)
        self.mem_size   = 2 ** self.addr_width
        self.db = {}

        """ Load content from secondary storage """
        try:
            with open(self.storage, "r") as ymlfile:
                self.db = yaml.load(ymlfile, Loader=yaml.BaseLoader)
        except IOError:
            logging.warning("DB file not exist, will create a new one")

    def __del__(self):
        self.mem_flush()

    def __addr_check(self, addr):
        res = True
        if addr & (self.byte_align - 1):
            logging.error("Address alignment: 0x%x", addr)
            res = False
        if addr > self.mem_size - self.byte_align:
            logging.error("Address is out of range: 0x%x", addr)
            res = False
        return res

    def mem_read(self, addr):
        if self.__addr_check(addr):
            hexaddr = hex(addr)
            if hexaddr not in self.db:
                logging.warning("Read uninitialized address: 0x%x", addr)
                data = int(random() * (2 ** self.data_width - 1) )
                self.db[hexaddr] = hex(data)
            else:
                data = int(self.db[hexaddr], 0)
            logging.info("Memmory read : [0x%04x] => 0x%x", addr, data)
            return data

    def mem_write(self, addr, data):
        if self.__addr_check(addr):
            logging.info("Memmory write: [0x%04x] <= 0x%x", addr, data)
            self.db[hex(addr)] = hex(data)

    """ Store content to secondary storage """
    def mem_flush(self):
        with open(self.storage, "w") as ymlfile:
            yaml.dump(self.db, ymlfile)
