#####################################################################
#                                                                   #
# /caching_utilities.py                                             #
#                                                                   #
# Copyright 2013, Monash University                                 #
#                                                                   #
# This file is part of the program lyse, in the labscript suite     #
# (see http://labscriptsuite.org), and is licensed under the        #
# Simplified BSD License. See the license.txt file in the root of   #
# the project for the full license.                                 #
#                                                                   #
#####################################################################

# enable caching for images and sequence Run objects
caching_enabled = True
cache_timeout = 0.1
cache_port = 16589

from zprocess import ZMQServer

class CacheServer(ZMQServer):
    def __init__(self, *args, **kwargs):
        super(CacheServer, self).__init__(*args, **kwargs)
        self.storage = {}

    def remove_data_by_filepath(self, filepath, dic=None):
        if dic is None:
            dic = self.storage

        # find top level keys
        if filepath in dic:
            del dic[filepath]

        # recursivly search the rest
        for k in dic.keys():
            if isinstance(dic[k], dict):
                self.remove_data_by_filepath(filepath, dic[k])

    def handler(self, request_data):
        # logger.info('CacheServer request: %s' % str(request_data))
        if isinstance(request_data, tuple):
            command, keys, data = request_data

            storage = self.storage
            if len(keys) > 1:
                for key in keys[:-1]:
                    if key not in storage:
                        storage[key] = {}
                    storage = storage[key]

            if command == "get":
                try:
                    return storage[keys[-1]]
                except KeyError:
                    return None
                except IndexError:
                    return storage

            elif command == "set":
                storage[keys[-1]] = data
                return True

            elif command == "del":
                try:
                    del storage[keys[-1]]
                except KeyError and IndexError:
                    return False
                return True

            elif command == "remove_shot":
                self.remove_data_by_filepath(data)
                return True

            # elif command == "clear":
            #     del self.storage
            #     self.storage = {}

        return ("error: operation not supported. Recognised requests are:\n "
                "(<get/set/del/clear>, <tuple_of_storage_keys>, <data_to_store>)")
