# -*- coding: utf-8 -*-

'''
Created on Jan 7, 2011

@author: Eduardo S. Scarpellini, <scarpellini@gmail.com>
'''

class ErrBase(Exception):
    """Base class for user defined exceptions
    """

    def __init__(self, msg=None, error=None, **kwargs):
        self._params = kwargs
        self.__dict__.update(self._params)

        if not self.__dict__.has_key("msg"):
            self.msg = msg

        if not self.__dict__.has_key("error"):
            self.error = error

    def __str__(self):
        try:
            return "%s - %s (%s)" % (self.msg, self.error, "; ".join(["%s = %s" % (k, repr(v))
                                                         for k, v in self._params.items()]))
        except:
            return "%s (%s)" % (self.__class__.__name__, self.__dict__)


class MongoConnException(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Error trying to connect to the MongoDB"

        super(MongoConnException, self).__init__(**kwargs)


class MongoDBException(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Error trying to get the MongoDB database"

        super(MongoDBException, self).__init__(**kwargs)


class MongoColException(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Error trying to get the MongoDB collection"

        super(MongoColException, self).__init__(**kwargs)


class MongoInsertException(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Error trying to insert data into MongoDB"

        super(MongoInsertException, self).__init__(**kwargs)


class MongoRemoveException(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Error trying remove data from MongoDB"

        super(MongoRemoveException, self).__init__(**kwargs)


class MongoFindException(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Error trying to find data on MongoDB"

        super(MongoFindException, self).__init__(**kwargs)


class MongoUpdateException(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Error trying to update data in MongoDB"

        super(MongoUpdateException, self).__init__(**kwargs)


class NodeNotFound(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Node not found"
        self.error = "ObjectID not found on MongoDB"

        super(NodeNotFound, self).__init__(**kwargs)


class EdgeNotFound(ErrBase):
    def __init__(self, **kwargs):
        self.msg = "Edge not found"
        self.error = "ObjectID not found on MongoDB"

        super(EdgeNotFound, self).__init__(**kwargs)
