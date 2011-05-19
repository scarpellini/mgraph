# -*- coding: utf-8 -*-

'''
Created on Dec 23, 2010

@author: Eduardo S. Scarpellini, <scarpellini@gmail.com>
'''


'''
TODO:
docstrings
tests
code review
draw? // matplotlib.pyplot, networkx
'''

#import logging
import mexceptions
import pymongo
from bson.objectid import ObjectId
from collections import deque


class MGraph(object):
    """Graph API with persistence on MongoDB
    
    >>> import mgraph
    >>>
    >>> g = mgraph.MGraph()
    >>>
    """

    _MONGO_CLASS = pymongo
    _MONGO = None
    DB_NAME = "graph"
    NODES_COLLECTION_NAME = "nodes"
    NODES_COLLECTION_INDEXES = ["name", "type"]
    EDGES_COLLECTION_NAME = "edges"
    EDGES_COLLECTION_INDEXES = ["out"]

    def __init__(self, host="localhost", port=27017):
        self._db_name = MGraph.DB_NAME
        self._nodes_collection_name = MGraph.NODES_COLLECTION_NAME
        self._nodes_collection_indexes = MGraph.NODES_COLLECTION_INDEXES
        self._edges_collection_name = MGraph.EDGES_COLLECTION_NAME
        self._edges_collection_indexes = MGraph.EDGES_COLLECTION_INDEXES

        self.mongo_host = host
        self.mongo_port = port

        self._mongo = self._get_mongo(self.mongo_host, self.mongo_port)
        self._mdb = self._get_db(self._mongo, self._db_name)
        self._nodes_col = self._get_col(self._mdb, self._nodes_collection_name)
        self._edges_col = self._get_col(self._mdb, self._edges_collection_name)

        self._ensure_indexes(self._nodes_col, self._nodes_collection_indexes)
        self._ensure_indexes(self._edges_col, self._edges_collection_indexes)

    def _get_mongo(self, host=None, port=None):
        """Return a _MONGO_CLASS.Connection() object instance (GLOBAL)
        """

        if not MGraph._MONGO:
            try:
                MGraph._MONGO = MGraph._MONGO_CLASS.Connection(host=host, port=port)
            except Exception, e:
                raise mexceptions.MongoConnException(error=e,
                                                     host=self.mongo_host, port=self.mongo_port)

        return MGraph._MONGO

    def _get_db(self, mongo=None, db_name=None):
        """Return a MongoDB database object instance
        """

        try:
            return mongo[db_name]
        except Exception, e:
            raise mexceptions.MongoDBException(error=e, host=self.mongo_host,
                                               port=self.mongo_port, database=db_name)

    def _get_col(self, db=None, collection_name=None):
        """Return a MongoDB collection object instance
        """

        try:
            return db[collection_name]
        except Exception, e:
            raise mexceptions.MongoColException(error=e, host=self.mongo_host,
                                               port=self.mongo_port, database=self._db_name,
                                               collection=collection_name)

    def _ensure_indexes(self, collection=None, indexes=None):
        """[Try to] Ensure indexes on MongoDB
        
        >>> import mgraph
        >>> g = mgraph.MGraph()
        >>>
        >>> g._ensure_indexes(g._edges_col, g._edges_collection_indexes)
        True
        >>> g._ensure_indexes(g._nodes_col, g._nodes_collection_indexes)
        True
        >>>
        """

        for index in indexes:
            collection.ensure_index(index)

        return True

    def _insert(self, collection=None, **kwargs):
        """[Try to] Insert data into MongoDB (safe)
        
        >>> import mgraph
        >>> g = mgraph.MGraph()
        >>>
        >>> nodes, edges = ([], [])
        >>>
        >>> for n in xrange(1, 100):
        ...     nodes.append(g._insert(g._nodes_col, { "id_int": n, "id_str": str(n) }))
        ...
        ...     if n > 1:
        ...         edges.append(g._insert(g._edges_col, { "_id": nodes[n],
        ...                                "out": { str(nodes[n-1]): { "attr_str": "X", "attr_int": 1 }}}))
        >>> len(nodes)
        99
        >>>
        >>> len(edges)
        99
        """

        kwargs["safe"] = True

        try:
            return collection.insert(**kwargs)
        except Exception, e:
            raise mexceptions.MongoInsertException(error=e, host=self.mongo_host,
                                               port=self.mongo_port, database=self._db_name,
                                               collection=collection.name, args=kwargs)

    def _find(self, collection=None, prefetch=False, **kwargs):
        """[Try to] Find data on MongoDB
        
        >>> import mgraph
        >>> g = mgraph.MGraph()
        >>>
        >>> a = []
        >>>
        >>> for n in xrange(1, 100):
        ...     a.append(g.add_node({ "id_int": n, "id_str": str(n) }))
        >>>
        >>> len(a)
        99
        """

        try:
            cursor = collection.find(**kwargs)

            if prefetch and type(cursor) != list:
                return [item for item in cursor]

            return cursor
        except Exception, e:
            raise mexceptions.MongoFindException(error=e, host=self.mongo_host,
                                               port=self.mongo_port, database=self._db_name,
                                               collection=collection.name, args=kwargs)

    def _get(self, collection=None, **kwargs):
        """[Try to] Find[_one] data on MongoDB
        """

        try:
            return collection.find_one(**kwargs)
        except Exception, e:
            raise mexceptions.MongoFindException(error=e, host=self.mongo_host,
                                               port=self.mongo_port, database=self._db_name,
                                               collection=collection.name, args=kwargs)

    def _update(self, collection=None, **kwargs):
        """[Try to] Update data in MongoDB (safe)
        """

        kwargs["safe"] = True

        try:
            return collection.update(**kwargs)
        except Exception, e:
            raise mexceptions.MongoUpdateException(error=e, host=self.mongo_host,
                                               port=self.mongo_port, database=self._db_name,
                                               collection=collection.name, args=kwargs)

    def _remove(self, collection=None, **kwargs):
        """[Try to] Remove data from MongoDB (safe)
        
        >>> len(a)
        99
        """

        kwargs["safe"] = True

        try:
            return collection.remove(**kwargs)
        except Exception, e:
            raise mexceptions.MongoRemoveException(error=e, host=self.mongo_host,
                                               port=self.mongo_port, database=self._db_name,
                                               collection=collection.name, args=kwargs)


    def _validate_objectid(self, id=None):
        """Validate ObjectId
        """

        if type(id) == ObjectId:
            return True

        return False

    def objectid(self, id=None):
        """Return an ObjectId object instance for id (str) 
        """

        if type(id) not in (str, unicode):
            raise TypeError("Unsupported type: id")

        return ObjectId(id)

    def objectid_repr(self, objectid=None):
        """Return the string 'representation' of ObjectId
        """

        if not self._validate_objectid(id=objectid):
            raise TypeError("Unsupported type: objectid")

        return str(objectid)

    def add_node(self, attrs=None):
        """Add a node to the database
        """

        if type(attrs) not in (dict, list):
            raise TypeError("Unsupported type: attrs")

        return self._insert(self._nodes_col, doc_or_docs=attrs)

    def update_node(self, node_id=None, attrs=None):
        """Update node attrs on the database
        """

        if not self._validate_objectid(id=node_id):
            raise TypeError("Unsupported type: node_id")

        if type(attrs) != dict:
            raise TypeError("Unsupported type: attrs")

        self._update(self._nodes_col,
                    spec={ "_id": node_id },
                    document={ "$set": attrs },
                    upsert=True)

        return True

    def remove_node(self, node_id=None):
        """Remove node from the database
        """

        if not self._validate_objectid(id=node_id):
            raise TypeError("Unsupported type: node_id")

        self._remove(self._nodes_col, spec_or_id=node_id)
        self._cleanup_edges(node_id=node_id)

        return True

    def find_nodes(self, where=None, attrs=None, skip=0, limit=0, prefetch=False):
        """Search for nodes
        """

        if type(where) != dict:
            raise TypeError("Unsupported type: where")

        if type(attrs) != list:
            raise TypeError("Unsupported type: attrs")

        if type(skip) != int:
            raise TypeError("Unsupported type: skip")

        if type(limit) != int:
            raise TypeError("Unsupported type: limit")

        if type(prefetch) != bool:
            raise TypeError("Unsupported type: prefetch")

        return self._find(self._nodes_col, spec=where, fields=attrs,
                          skip=skip, limit=limit, prefetch=prefetch)

    def get_node(self, node_id=None):
        """Fetch node attrs
        """

        if not self._validate_objectid(id=node_id):
            raise TypeError("Unsupported type: node_id")

        return self._get(self._nodes_col, spec_or_id=node_id)

    def has_node(self, spec=None):
        """Check node existence
        """

        if self._validate_objectid(spec):
            spec = { "_id": spec }

        if self._get(self._nodes_col, spec_or_id=spec, fields=["_id"]):
            return True

        return False

    def has_edge(self, from_node=None, to_node=None):
        """Check edge existence
        """

        if not self._validate_objectid(id=from_node):
            raise TypeError("Unsupported type: from_node")

        if not self._validate_objectid(id=to_node):
            raise TypeError("Unsupported type: to_node")

        spec = { "_id": from_node }

        # adjust spec (where)
        if to_node:
            spec[str(to_node)] = { "$exists": "true" }

        # out-edges
        if self._get(self._edges_col, spec_or_id=spec, fields=["_id"]):
            return True

        # in-edges (only if to_node is None)
        if self._get(self._edges_col,
                     spec_or_id={str(from_node): { "$exists": "true" }},
                    fields=["_id"]):
            return True

        return False

    def get_node_edges(self, node_id=None, direction="both"):
        """Fetch node edges and its attrs
        """

        if not self._validate_objectid(id=node_id):
            raise TypeError("Unsupported type: node_id")

        if direction not in ("in", "out", "both"):
            raise AttributeError("Unsupported value: direction")

        edges = { "_id": node_id }

        if direction in ("in", "both"):
            edges["in"] = {}

            in_edges = self._find(self._edges_col,
                                  spec_or_id={ str(node_id): { "$exists": "true" } })

            for edge in in_edges:
                if not edge.has_key(str(node_id)):
                    continue

                edge[str(node_id)]["_from_id"] = edge["_id"]
                del edge[str(node_id)]["_to_id"]
                edges["in"][str(edge["_id"])] = edge[str(node_id)]

        if direction in ("out", "both"):
            edges["out"] = {}

            out_edges = self._get(self._edges_col, spec_or_id=node_id)

            if out_edges:
                del out_edges["_id"]
                edges["out"] = out_edges

        return edges

    def add_edge(self, from_node=None, to_node=None, attrs=None):
        """Add a edge between two given nodes (update_edge() wrapper)
        """

        return self.update_edge(from_node=from_node, to_node=to_node, attrs=attrs)

    def update_edge(self, from_node=None, to_node=None, attrs=None):
        """[Try to] Create/Update edge and its attrs.
        """

        if not attrs:
            attrs = {}

        if not self._validate_objectid(id=from_node):
            raise TypeError("Unsupported type: from_node")

        if not self._validate_objectid(id=to_node):
            raise TypeError("Unsupported type: to_node")

        if type(attrs) != dict:
            raise TypeError("Unsupported type: attrs")

        if not self.has_node(from_node):
            raise mexceptions.NodeNotFound("Node not found: from_node")

        if not self.has_node(to_node):
            raise AttributeError("Node not found: to_node")

        attrs["_to_id"] = to_node

        self._update(self._edges_col,
                     spec={ "_id": from_node },
                     document={ "$set":
                               dict(
                                    [(str(to_node) + "." + str(key), value)
                                     for key, value in attrs.items()])
                               },
                     upsert=True)

        return True

    def remove_edge(self, from_node=None, to_node=None):
        """Remove edge between two nodes
        """

        if not self._validate_objectid(id=from_node):
            raise TypeError("Unsupported type: from_node")

        if not self._validate_objectid(id=to_node):
            raise TypeError("Unsupported type: to_node")

        self._update(self._edges_col,
                     spec={ "_id": from_node },
                     document={ "$unset": { str(to_node): 1 }})

        return True

    def _cleanup_edges(self, node_id=None, force=False):
        """[Try to] Cleanup 'in' and 'out' edges
        """

        if not self._validate_objectid(id=node_id):
            raise TypeError("Unsupported type: node_id")

        if self.has_node(node_id) and not force:
            return False

        remove_ok = True

        try:
            self._remove(self._edges_col, spec_or_id=node_id)
        except:
            remove_ok = False

        try:
            self._update(self._edges_col,
                         spec={ str(node_id): { "$exists": "true" } },
                         document={ "$unset": { str(node_id): 1 }},
                         multi=True)
        except:
            remove_ok = False

        return remove_ok


class Traverser(object):
    """Simple MGraph graph traverser
    """

    def __init__(self, mongodao=None):
        self._mongodao = mongodao

    def bfs(self, from_node=None):
        """Breadth-first search (iterator)
        """

        if not self._mongodao._validate_objectid(id=from_node):
            raise TypeError("Unsupported type: from_node")

        if not self._mongodao.has_node(from_node):
            raise AttributeError("Node not found: from_node")

        queue = deque([(None, from_node)])
        nodes = []

        while queue:
            parent, me = queue.popleft()

            if not self._mongodao.has_node(me):
                continue

            if not me in nodes:
                nodes.append(me)

                queue.extend([(me, self._mongodao.objectid(child)) for child in
                             self._mongodao.get_node_edges(node_id=me, direction="out")["out"].keys()
                             if child != me])

            if not parent:
                continue

            yield (self._mongodao.get_node(parent), self._mongodao.get_node(me))

    def dfs(self, from_node=None):
        """Depth-first search (iterator)
        """

        if not self._mongodao._validate_objectid(id=from_node):
            raise TypeError("Unsupported type: from_node")

        if not self._mongodao.has_node(from_node):
            raise AttributeError("Node not found: from_node")

        stack = deque([(None, from_node)])
        nodes = []

        while stack:
            parent, me = stack.pop()

            if not self._mongodao.has_node(me):
                continue

            if not me in nodes:
                nodes.append(me)

                stack.extend([(me, self._mongodao.objectid(child)) for child in
                             self._mongodao.get_node_edges(node_id=me, direction="out")["out"].keys()
                             if child != me])

            if not parent:
                continue

            yield (self._mongodao.get_node(parent), self._mongodao.get_node(me),)


    def shortest_path(self, from_node=None, to_node=None):
        """Shortest path between two nodes (use bfs())
        """

        if not self._mongodao._validate_objectid(id=from_node):
            raise TypeError("Unsupported type: from_node")

        if not self._mongodao._validate_objectid(id=to_node):
            raise TypeError("Unsupported type: to_node")

        #if not self._mongodao.has_node(from_node):
        #    raise AttributeError("Node not found: from_node")

        if not self._mongodao.has_node(to_node):
            raise AttributeError("Node not found: to_node")

        paths = {}

        for parent, me in self.bfs(from_node=from_node):
            prefix = []

            if paths.has_key(str(parent["_id"])):
                prefix = paths[str(parent["_id"])]

            paths[str(me["_id"])] = prefix + [me]

            if me["_id"] == to_node:
                return paths[str(me["_id"])]

        return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
