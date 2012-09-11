# -*- coding: utf-8 -*-

import server

class ServerList(list):
    def __init__(self):
        super(ServerList, self).__init__([])

    def __repr__(self):
        return '<ServerList: {0}>'.format(len(self))
        
    def append(self, item):
        if not isinstance(item, server.Server):
            raise TypeError('item must be from type Server')
        if not any(map(lambda obj: obj == item, self)):
            super(ServerList, self).append(item)
