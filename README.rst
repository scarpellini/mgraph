======
MGraph
======

A simple implementation of directed graph (http://en.wikipedia.org/wiki/Directed_graph) using MongoDB.
Both nodes and edges are MongoDB documents (each one in its own collections) and support any JSON attributes.



Examples:
--------


Adding Nodes:
=============

::
>>> import mgraph
>>> 
>>> g = mgraph.MGraph()
>>> 
>>> f = g.add_node({"name": "f"})
>>> d = g.add_node({"name": "d"})
>>> e = g.add_node({"name": "e"})
>>> s = g.add_node({"name": "s"})
>>> 
>>> f
ObjectId('4dd49c6f2041095cbc000000')
>>> s
ObjectId('4dd49c832041095cbc000003')
>>>
>>>
>>>
>>> xxx = g.add_node(
...    { "name": "xxx",
...      "type": "P",
...      "country": "BR",
...      "cities": ["Sao Paulo", "Rio de Janeiro"],
...      "phone": {
...            "mobile":  "+551112345678"}
...    })
>>>


Checking node existence:
>>> g.has_node(g.objectid("4dd49c782041095cbc000002"))
True
>>>
>>> g.has_node(g.objectid("4dd49c782041095cbc00000d"))
False


Getting one node:
>>> g.get_node(f)
{u'_id': ObjectId('4dd49c6f2041095cbc000000'), u'name': u'f'}
>>> g.get_node(s)
{u'_id': ObjectId('4dd49c832041095cbc000003'), u'name': u's'}


Finding nodes:
>>> [n for n in g.find_nodes(where={"name": "s"}, attrs=["_id", "name"])]
[{u'_id': ObjectId('4dd49c832041095cbc000003'), u'name': u's'}]
>>> [n for n in g.find_nodes(where={"name": "f"}, attrs=["_id", "name"])]
[{u'_id': ObjectId('4dd49c6f2041095cbc000000'), u'name': u'f'}]


Adding edges:
>>> g.add_edge(f, d)
True
>>> g.add_edge(f, e)
True
>>> g.add_edge(d, s)
True


Getting edges:
>>> g.get_node_edges(f)
{'_id': ObjectId('4dd49c6f2041095cbc000000'), 'out': {u'4dd49c782041095cbc000002': {u'_to_id': ObjectId('4dd49c782041095cbc000002')}, u'4dd49c732041095cbc000001': {u'_to_id': ObjectId('4dd49c732041095cbc000001')}}, 'in': {}}
>>>
>>> g.get_node_edges(d, direction="out")
{'_id': ObjectId('4dd49c732041095cbc000001'), 'out': {u'4dd49c832041095cbc000003': {u'_to_id': ObjectId('4dd49c832041095cbc000003')}}}
>>>
>>> g.get_node(xxx)
{u'cities': [u'Sao Paulo', u'Rio de Janeiro'], u'name': u'xxx', u'country': u'BR', u'phone': {u'mobile': u'+551112345678'}, u'_id': ObjectId('4dd4a1982041095cbc000008'), u'type': u'P'}
>>> 




Traverser:
- Breadth-first search (iterator)
>>> [n for n in t.bfs(f)]
[({u'_id': ObjectId('4dd49c6f2041095cbc000000'), u'name': u'f'}, {u'_id': ObjectId('4dd49c782041095cbc000002'), u'name': u'e'}), ({u'_id': ObjectId('4dd49c6f2041095cbc000000'), u'name': u'f'}, {u'_id': ObjectId('4dd49c732041095cbc000001'), u'name': u'd'}), ({u'_id': ObjectId('4dd49c732041095cbc000001'), u'name': u'd'}, {u'_id': ObjectId('4dd49c832041095cbc000003'), u'name': u's'})]

- Depth-first search (iterator)
>>> [n for n in t.dfs(f)]
[({u'_id': ObjectId('4dd49c6f2041095cbc000000'), u'name': u'f'}, {u'_id': ObjectId('4dd49c732041095cbc000001'), u'name': u'd'}), ({u'_id': ObjectId('4dd49c732041095cbc000001'), u'name': u'd'}, {u'_id': ObjectId('4dd49c832041095cbc000003'), u'name': u's'}), ({u'_id': ObjectId('4dd49c6f2041095cbc000000'), u'name': u'f'}, {u'_id': ObjectId('4dd49c782041095cbc000002'), u'name': u'e'})]

- Shortest path
>>> t.shortest_path(f, s)
[{u'_id': ObjectId('4dd49c732041095cbc000001'), u'name': u'd'}, {u'_id': ObjectId('4dd49c832041095cbc000003'), u'name': u's'}]
