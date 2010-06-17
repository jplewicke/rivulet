# -*- coding: utf-8 -*-

# Copyright (c) 2008-2009 "Neo Technology,"
#     Network Engine for Objects in Lund AB [http://neotechnology.com]
# 
# This file is part of Neo4j.py.
# 
# Neo4j.py is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Neo4j domain modeling for Django

 This module contains the necessary classes for defining domain models
 for Django based on storage in Neo4j.


 Copyright (c) 2009 "Neo Technology,"
     Network Engine for Objects in Lund AB [http://neotechnology.com]
"""

__all__ = 'NodeModel', 'Relationship', 'Property', 'Incoming', 'Outgoing'

from neo4j.__bootstrap__ import __bootstrap__

# Things that would be nice to create models for (builtin models in django):
# * django.contrib.auth.models
#   - by creating a module for it and allow override of
#     settings.AUTHENTICATION_BACKENDS

@__bootstrap__
def __bootstrap__(pyneo):
    global NodeModel, Relationship, Property # XXX: move these inwards
    global NeoServiceProperty, Incoming, Outgoing

    try:
        from django.db import models as django
        from django.db.models.fields.related import add_lazy_relation
    except:
        import traceback; traceback.print_exc()
        raise ImportError(
            "The Django models for Neo4j can only be used from within Django.")
    from neo4j import Incoming, Outgoing, transactional
    import itertools

    class NeoServiceProperty(object):
        def __get__(self, obj, cls=None):
            return DjangoNeo.neo

    class not_implemented(object):
        def __init__(self, method):
            self.__method = method
            if method.__doc__:
                self.__doc = "\n" + method.__doc__
            else:
                self.__doc = ''
            self.__repr = method.__name__
        def contribute_to_class(self, cls, name):
            self.set_repr(cls, name)
            setattr(cls, name, self)
        def set_repr(self, cls, name):
            self.__repr = '<%s>.%s()' % (cls.__name__, name)
        def __get__(self, obj, cls):
            if obj is None:
                return self
            if not '.' in self.__repr:
                if cls is None: cls = type(obj)
                self.set_repr(cls, self.__repr)
            def closure(*args, **kwargs):
                self(obj, *args, **kwargs)
            return closure
        def __call__(self, *args, **kwargs):
            self.__method(*args, **kwargs) # this is to verify signature
            raise NotImplementedError(self.__repr + self.__doc)

    transactional = transactional(NeoServiceProperty())

    class LazyModel(object):
        def __init__(self, cls, field, name, setup_reversed):
            add_lazy_relation(cls, field, name, self.__setup)
            self.__setup_reversed = setup_reversed
        def __setup(self, field, target, source):
            if not issubclass(target, NodeModel):
                raise TypeError("Relationships may only extend from Nodes.")
            self.__target = target
            self.__setup_reversed(target)
        __target = None
        @property
        def __model(self):
            model = self.__target
            if model is None:
                raise ValueError("Lazy model not initialized!")
            else:
                return model
        def __getattr__(self, attr):
            return getattr(self.__model, attr)
        def __call__(self, *args, **kwargs):
            return self.__model(*args, **kwargs)

    class DjangoNeo(object):
        def __init__(self):
            self.__field_counter = 0
        @property
        def field_counter(self):
            res = self.__field_counter
            self.__field_counter += 1
            return res

        @property
        def neo(self):
            try:
                return self.__neo
            except:
                return self.__setup_neo()
        def __setup_neo(self):
            from django.conf import settings
            from neo4j import NeoService
            import os
            try:
                resource_uri = settings.NEO4J_RESOURCE_URI
                assert resource_uri, "the resource_uri must be defined"
            except:
                raise ValueError("NEO4J_RESOURCE_URI is not defined in "
                                 "the settings module.")
            options = getattr(settings, 'NEO4J_OPTIONS', {})
            self.__neo = NeoService(resource_uri, **options)
            return self.__neo

        def index(self, propname): # TODO: add the ability to choose index type
            return self.neo.index(propname, create=True)

        @transactional
        def type_node(self, app_label, model_name):
            for relationship in self.neo.reference_node.type_node:
                if (relationship['app_label'] == app_label and
                    relationship['model_name'] == model_name):
                    type_node = relationship.end
                    break
            else:
                type_node = self.neo.node()
                self.neo.reference_node.type_node(type_node,
                                                  app_label=app_label,
                                                  model_name=model_name,)
            return type_node

        @transactional
        def apply_to_buffer(self, constructor, items, size=1):
            result = [constructor(item) for item in
                      itertools.takewhile(countdown(size), items)]
            if not result:
                raise StopIteration
            return result

        @property
        def log(self):
            if False:
                pass
            else:
                return self.__log
        class __log(object):
            def __getattr__(self, attr):
                def logger(message, *args, **kwargs):
                    pass
                logger.__name__ = attr
                return logger
        __log = __log()
    DjangoNeo = DjangoNeo() # singleton

    def write_through(obj):
        return getattr(getattr(obj,'_meta',None),'write_through', False)

    def all_your_base(cls, base):
        if issubclass(cls, base):
            yield cls
            for parent in cls.__bases__:
                for cls in all_your_base(parent, base):
                    yield cls

    def countdown(number):
        counter = itertools.count()
        def done(*junk):
            for count in counter:
                return count < number
        return done

    def buffer_iterator(constructor, items, size=1):
        items = iter(items) # make sure we have an iterator
        while 1:
            for item in DjangoNeo.apply_to_buffer(constructor, items, size):
                yield item

    @pyneo.make
    def NodeModel():
        class NodeModelManager(django.Manager):
            def get_query_set(self):
                return NodeQuerySet(self.model)

            @not_implemented
            def _insert(self, values, **kwargs):
                pass
            @not_implemented
            def _update(self, values, **kwargs):
                pass

        class IdProperty(object):
            def __init__(self, getter, setter):
                self.getter = getter
                self.setter = setter
            def __get__(self, inst, cls):
                if inst is None: return IdLookup(cls)
                else:
                    return self.getter(inst)
            def __set__(self, inst, value):
                return self.setter(inst, value)
        class IdLookup(object):
            indexed = True
            unique = True
            def __init__(self, model):
                self.__model = model
            index = property(lambda self: self)
            def to_neo(self, value):
                return int(value)
            def nodes(self, nodeid):
                try:
                    node = DjangoNeo.neo.node[nodeid]
                except:
                    node = None
                else:
                    type_node = DjangoNeo.type_node(
                        self.__model._meta.app_label, self.__model.__name__)
                    for rel in node.relationships('<<INSTANCE>>').incoming:
                        # verify that the found node is an instance of the
                        # requested type
                        if rel.start == type_node: break # ok, it is!
                    else: # no, it isn't!
                        node = None
                if node is not None:
                    yield node

        class NodeModel(django.Model):
            """Extend to make models"""
            objects = NodeModelManager()
            class Meta:
                abstract = True

            @classmethod
            def _neo4j_instance(cls, node):
                instance = cls.__new__(cls)
                instance.__node = node
                return instance

            #def __init__(self, *args, **kwargs):
            #    self.__node = Neo4jDjangoModel.neo.node()
            #    super(NodeModel, self).__init__(*args, **kwargs)

            def _get_pk_val(self, meta=None):
                return self.__node.id
            def _set_pk_val(self, value):
                if self.__node is None and value is None: return
                raise TypeError("Cannot change the id of nodes.")
            pk = id = IdProperty(_get_pk_val, _set_pk_val)

            def __eq__(self, other):
                try:
                    return self.__node == other.__node
                except:
                    return False

            __node = None
            @property
            def node(self):
                node = self.__node
                if node is None:
                    # XXX: come up with a better exception type
                    raise ValueError("Unsaved objects have no nodes.")
                else:
                    return node
            _neo4j_underlying = node

            @transactional
            def save_base(self, raw=False, cls=None, origin=None,
                          force_insert=False, force_update=False):
                assert not (force_insert and force_update)
                if cls:
                    DjangoNeo.log.debug("save_base: cls=%s", cls)
                if origin:
                    DjangoNeo.log.debug("save_base: origin=%s", origin)
                self._save_neo4j_node()
                self._save_neo4j_Properties(self, self.__node)
                self._save_neo4j_Relationships(self, self.__node)
            save_base.alters_data = True

            @transactional
            def _save_neo4j_node(self):
                if self.__node is None:
                    self.__node = node = DjangoNeo.neo.node()
                    for type_node in self.__all_type_nodes():
                        type_node.relationships('<<INSTANCE>>')(node)
                return self.__node
            _save_neo4j_node.alters_data = True

            @classmethod
            def _neo4j_type_node(cls):
                assert not cls == NodeModel, "only defined models have a type"
                try:
                    node = cls.__type_node
                except:
                    node=DjangoNeo.type_node(cls._meta.app_label,cls.__name__)
                    cls.__type_node = node
                return node

            @classmethod
            def __all_type_nodes(cls):
                for cls in all_your_base(cls, NodeModel):
                    if cls != NodeModel:
                        yield cls._neo4j_type_node()

            def _collect_sub_objects(self,seen_objs,parent=None,nullable=False):
                raise TypeError(
                    "NodeModel does not support _collect_sub_objects")

            @transactional
            @not_implemented
            def delete(self):
                pass
            delete.alters_data = True

            @transactional
            def _get_next_or_previous_by_FIELD(self, field, is_next, **kwargs):
                raise NotImplementedError("<NodeModel>.next/previous by %s" %
                                          field.attname)
            @transactional
            def _get_next_or_previous_in_order(self, is_next):
                raise NotImplementedError("<NodeModel>.next/previous")

        class NodeQuerySet(object):
            def __init__(self, model):
                self.model = model
            def __nodes(self):
                type_node = self.model._neo4j_type_node()
                for relationship in type_node.relationships('<<INSTANCE>>'):
                    yield relationship.end
            def __iter__(self):
                return buffer_iterator(self.model._neo4j_instance,
                                       self.__nodes(), size=10)
            # count
            # dates
            # distinct
            # extra
            def create(self, **kwargs):
                obj = self.model(**kwargs)
                obj.save(force_insert=True)
                return obj
            @transactional
            def get(self, **lookup):
                resultset = self
                indexes = []
                index = None
                for key, value in lookup.items():
                    if value is None: continue # None cannot be used in indexes
                    attribute = getattr(self.model, key)
                    if attribute.indexed:
                        if attribute.unique:
                            index = attribute.index
                            break
                        else:
                            indexes.append((key, attribute.index))
                else:
                    if indexes:
                        # XXX: select most appropriate index based on
                        #      number of entries for the key
                        key, index = indexes.pop()
                if index:
                    value = lookup.pop(key)
                    value = attribute.to_neo(value)
                    resultset = index.nodes(value)
                if lookup:
                    # TODO: filter for the remaining ones
                    raise NotImplementedError("filtering of query set")
                result = None
                for item in resultset:
                    if result is not None:
                        if index: lookup[key] = value
                        raise self.model.MultipleObjectsReturned(
                            "get() returned more than one %s. "
                            "Lookup parameters were %s" % 
                            (self.model._meta.object_name, lookup))
                    else:
                        result = item
                if result is None:
                    if index: lookup[key] = value
                    raise self.model.DoesNotExist(
                        "%s matching query does not exist."
                        "Lookup parameters were %s" % 
                        (self.model._meta.object_name, lookup))
                return self.model._neo4j_instance(result)
            # get_or_create
            # filter
            # aggregate
            # annotate
            # complex_filter
            # exclude
            # in_bulk
            # iterator
            # latest
            # latest
            # order_by
            # select_related
            # values
            # values_list
            # update
            # reverse
            # defer
            # only

        return NodeModel

    @pyneo.make
    def Relationship():
        class Meta(type):
            def __new__(meta, name, bases, body):
                new = super(Meta, meta).__new__
                parents = [cls for cls in bases if isinstance(cls, Meta)]
                if not parents: # this is the base class
                    return new(meta, name, bases, body)
                module = body.pop('__module__')
                modelbases = [cls.Model for cls in parents
                              if hasattr(cls, 'Model')]
                Model = RelationshipModel.new(module, name, modelbases)
                for key, value in body.items():
                    if hasattr(value, 'contribute_to_class'):
                        value.contribute_to_class(Model, key)
                    else:
                        setattr(Model, key, value)
                return new(meta, name, bases, {
                        '__module__': module,
                        'Model': Model,
                    })
            def __getattr__(cls, key):
                if hasattr(cls, 'Model'):
                    return getattr(cls.Model, key)
                else:
                    raise AttributeError(key)
            def __setattr__(cls, key, value):
                if hasattr(cls, 'Model'):
                    setattr(cls.Model, key, value)
                else:
                    raise TypeError(
                        "Cannot assign attributes to base Relationship")

        class RelationshipModel(object):
            __relationship = None
            def __init__(self):
                pass
            @property
            def relationship(self):
                rel = self.__relationship
                if rel is None:
                    # XXX: better exception
                    raise ValueError("Unsaved objects have no relationship.")
                else:
                    return rel
            _neo4j_underlying = relationship
            @classmethod
            def new(RelationshipModel, module, name, bases):
                return type(name, bases + [RelationshipModel], {
                        '__module__': module,})
            @classmethod
            def add_field(self, prop):
                raise NotImplementedError("<RelationshipModel>.add_field()")

        class Relationship(object):
            """Extend to add properties to relationships."""
            __metaclass__ = Meta

            def __init__(self, target, type=None, direction=None, optional=True,
                         single=False, related_single=False, related_name=None):
                if related_name is None:
                    if related_single:
                        related_name = '%(name)s'
                    else:
                        related_name = '%(name)s_set'
                if not pyneo.python.is_string(type):
                    if direction is not None:
                        if type.direction is not direction:
                            raise TypeError("Incompatiable direction!")
                    else:
                        direction = type.direction
                    type = type.type
                self.__target = target
                self.__name = type
                self.__single = single
                self._direction = direction
                self.creation_counter = DjangoNeo.field_counter
                self.__related_single = related_single
                self.reversed_name = related_name
            target = property(lambda self: self.__target)

            __is_reversed = False
            def reverse(self, target, name):
                if self._direction is Incoming:
                    direction = Outgoing
                elif self._direction is Outgoing:
                    direction = Incoming
                else:
                    direction = None
                relationship = Relationship(
                    target, type=self.__name, direction=direction,
                    single=self.__related_single, related_name=name)
                relationship.__is_reversed = True
                return relationship

            def contribute_to_class(self, source, name):
                if not issubclass(source, NodeModel):
                    raise TypeError("Relationships may only extend from Nodes.")
                if pyneo.python.is_string(self.__target):
                    target = LazyModel(source, self, self.__target,
                             lambda target: bound._setup_reversed(target))
                else:
                    target = self.__target
                if hasattr(self, 'Model'):
                    if self.__single:
                        Bound = SingleRelationship
                    else:
                        Bound = MultipleRelationships
                    bound = Bound(self, source, self.__name or name, name,
                                  self.Model)
                else:
                    if self.__single:
                        Bound = SingleNode
                    else:
                        Bound = MultipleNodes
                    bound = Bound(self, source, self.__name or name, name)
                source._meta.add_field(bound)
                setattr(source, name, bound)
                if not self.__is_reversed:
                    bound._setup_reversed(target)

        class BoundRelationship(object):
            indexed = False
            rel = None
            primary_key = False
            choices = None
            db_index = None
            def __init__(self, rel, source, relname, attname):
                self.__rel = rel
                self.__source = source
                self._type = relname
                self.__attname = attname
                relationships = self.__relationships_for(source)
                relationships[self.name] = self # XXX weekref
            def _setup_reversed(self, target):
                self.__target = target
                if not isinstance(target, LazyModel):
                    self.__rel.reverse(self.__source,
                                       self.__attname).contribute_to_class(
                        target, self.__reversed_name)
            attname = name = property(lambda self: self.__attname)
            _direction = property(lambda self: self.__rel._direction)
            _target_model = property(lambda self: self.__rel.target)
            __reversed_name = property(lambda self: self.__rel.reversed_name)

            def get_default(self):
                return None

            @staticmethod
            def __state_for(instance, create=True):
                try:
                    state = instance.__state
                except:
                    state = {}
                    if create:
                        instance.__state = state
                return state

            @staticmethod
            def __relationships_for(obj_or_cls):
                meta = obj_or_cls._meta
                try:
                    relationships = meta.__relationships
                except:
                    meta.__relationships = relationships = {}
                return relationships

            def _save_(instance, node):
                state = BoundRelationship.__state_for(instance, create=False)
                if state:
                    rels = BoundRelationship.__relationships_for(instance)
                    for key, value in state.items():
                        rels[key]._save_relationship(instance, node, value)
            NodeModel._save_neo4j_Relationships = staticmethod(_save_)
            del _save_
            @not_implemented
            def _save_relationship(self, instance, node, state):
                pass

            def _get_all_relationships(self, node):
                return self.__load_relationships(node)
            def __load_relationships(self, this):
                relationships = this.relationships(self._type)
                if self._direction is Incoming:
                    relationships = relationships.incoming
                elif self._direction is Outgoing:
                    relationships = relationships.outgoing
                return relationships

            creation_counter = property(lambda self:self.__rel.creation_counter)
            def __cmp__(self, other):
                return cmp(self.creation_counter, other.creation_counter)

            def __get__(self, obj, cls=None):
                if obj is None: return self
                return self._get_relationship(obj, self.__state_for(obj))

            def __set__(self, obj, value):
                self._set_relationship(obj, self.__state_for(obj), value)

            def __delete__(self, obj):
                self._del_relationship(obj, self.__state_for(obj))

            def _set_relationship(self, obj, state, value):
                if value is None: # assume initialization - ignore
                    return # TODO: verify that obj is unsaved!
                raise TypeError("<%s>.%s is not assignable" %
                                (obj.__class__.__name__, self.name))

            def _del_relationship(self, obj, state):
                raise TypeError("Cannot delete <%s>.%s" %
                                (obj.__class__.__name__, self.name))

        class SingleNode(BoundRelationship):
            def _get_relationship(self, obj, state):
                if self.name in state:
                    changed, result = state[self.name]
                else:
                    try:
                        this = obj.node
                    except:
                        result = None
                    else:
                        result = self.__load_related(this)
                    state[self.name] = False, result
                return result
            @transactional
            def __load_related(self, this):
                relationship = self.__load_relationships(this).single
                if relationship is None:
                    return None
                return self._neo4j_instance(this, relationship)

            def _neo4j_instance(self, this, relationship):
                that = relationship.getOtherNode(this)
                return self._target_model._neo4j_instance(that)

            def __load_relationships(self, this):
                relationships = this.relationships(self._type)
                if self._direction is Incoming:
                    relationships = relationships.incoming
                elif self._direction is Outgoing:
                    relationships = relationships.outgoing
                return relationships

            def _del_relationship(self, obj, state):
                self._set_relationship(obj, state, None)

            def _set_relationship(self, obj, state, other):
                state[self.name] = True, other

            def _save_relationship(self, instance, node, state):
                changed, other = state
                if not changed: return
                if other is None:
                    del self.__load_relationships(node).single
                else:
                    relationships = self.__load_relationships(node)
                    relationships.single = other._save_neo4j_node()

        class BoundRelationshipModel(BoundRelationship):
            def __init__(self, rel, cls, relname, attname, Model):
                super(BoundRelationship, self).__init__(
                    rel, cls, relname, attname)
                self.Model = Model
                raise NotImplementedError("Support for extended relationship "
                                          "models is not implemented yet.")

        class SingleRelationship(BoundRelationshipModel): # WAIT!
            @not_implemented
            def _get_relationship(self, obj, state):
                pass
            @not_implemented
            def _set_relationship(self, obj, state, other):
                pass

        class MultipleNodes(BoundRelationship):
            def _get_relationship(self, obj, states):
                state = states.get(self.name)
                if state is None:
                    states[self.name] = state = RelationshipInstance(self, obj)
                return state
                #return RelationshipInstance(self, obj, state)
                #this = obj.node
                #for rel in this.relationships(self._type):
                #    that = rel.getOtherNode(this)
                #    yield self._NodeModel(that)
            def _neo4j_instance(self, this, relationship):
                that = relationship.getOtherNode(this)
                return self._target_model._neo4j_instance(that)
            def accept(self, obj):
                pass # TODO: implement verification
            def _save_relationship(self, instance, node, state):
                state.__save__(node)
            def _create_relationship(self, node, obj):
                other = obj._save_neo4j_node()
                # TODO: verify that it's ok in the reverse direction
                self.__load_relationships(node)( other )
            def __load_relationships(self, this):
                relationships = this.relationships(self._type)
                if self._direction is Incoming:
                    relationships = relationships.incoming
                elif self._direction is Outgoing:
                    relationships = relationships.outgoing
                return relationships
            @not_implemented
            def _extract_relationship(self, obj):
                pass

        class MultipleRelationships(BoundRelationshipModel): # WAIT!
            @not_implemented
            def _get_relationship(self, obj, state):
                pass
            @not_implemented
            def add(self, obj, other):
                pass

        class RelationshipInstance(django.Manager):
            def __init__(self, rel, obj):
                self.__rel = rel
                self.__obj = obj
                self.__added = [] # contains domain objects
                self.__removed = pyneo.python.set() # contains relationships
            def __save__(self, node):
                for relationship in self.__removed:
                    relationship.delete()
                for obj in self.__added:
                    self.__rel._create_relationship(node, obj)
                self.__removed.clear()
                self.__added[:] = []
            def _neo4j_relationships(self, node):
                for rel in self.__rel._get_all_relationships(node):
                    if rel not in self.__removed:
                        yield rel
            @property
            def _new(self):
                for item in self.__added:
                    yield item
            def add(self, *objs):
                for obj in objs:
                    self.__rel.accept(obj)
                self.__added.extend(objs)
            def remove(self, *objs):
                for obj in objs:
                    self.__removed.add( self.__rel._extract_relationship(obj) )
            @not_implemented
            def clear(self):
                pass
            @not_implemented
            def create(self, *args, **kwargs):
                pass
            @not_implemented
            def get_or_create(self, *args, **kwargs):
                pass
            def get_query_set(self):
                return RelationshipQuerySet(self, self.__rel, self.__obj)

        class RelationshipQuerySet(object):
            def __init__(self, inst, rel, obj):
                self.__inst = inst
                self.__rel = rel
                self.__obj = obj
            def __relationships(self, node):
                for rel in self.__inst._neo4j_relationships(node):
                    if self.__keep_relationship(rel):
                        yield rel
            def __iter__(self):
                try:
                    node = self.__obj.node
                except:
                    pass
                else:
                    buffered = buffer_iterator(
                        lambda rel: self.__rel._neo4j_instance(node, rel),
                        self.__relationships(node), size=10)
                    for item in buffered:
                        yield item
                for item in self.__inst._new:
                    if self.__keep_instance(item):
                        yield item
            def __keep_instance(self, obj):
                return True # TODO: filtering
            def __keep_relationship(self, rel):
                return True # TODO: filterning
            @not_implemented
            def get(self, **lookup):
                pass

        return Relationship

    @pyneo.make
    def Property():
        class Property(object):
            """Extend to create properties of specific types."""
            def __init__(self,indexed=False,unique=False,type=None,name=None):
                self.indexed = indexed
                self.unique = unique
                self.__name = name
                self.creation_counter = DjangoNeo.field_counter

            @property
            def default(self):
                return None # TODO: perhaps add better code here

            def to_neo(self, value):
                return value
            def from_neo(self, value):
                return value

            def contribute_to_class(self, cls, name):
                if issubclass(cls, NodeModel):
                    prop = BoundProperty(self, cls, self.__name or name, name)
                    cls._meta.add_field(prop)
                elif issubclass(cls, Relationship):
                    if self.indexed:
                        raise TypeError(
                            "Relationship properties may not be indexed.")
                    prop = BoundProperty(self, cls, self.__name or name)
                    cls.add_field(prop)
                else:
                    raise TypeError("Properties may only be added to Nodes"
                                    " or Relationships")
                setattr(cls, name, prop)

        class BoundProperty(object):
            rel = None
            primary_key = False
            choices = None # TODO: add support for this
            def __init__(self, property, cls, propname, attname):
                self.__property = property
                self.__class = cls
                self.__propname = propname
                self.__attname = attname
                properties = self.__properties_for(cls)
                properties[self.name] = self # XXX: weakref
            creation_counter = property(lambda self:
                                            self.__property.creation_counter)
            attname = name = property(lambda self: self.__attname)
            convert = property(lambda self: self.__property.convert)
            indexed = db_index = property(lambda self: self.__property.indexed)
            unique = property(lambda self: self.__property.unique)
            to_neo = property(lambda self: self.__property.to_neo)
            from_neo = property(lambda self: self.__property.from_neo)
            @property
            def index(self):
                if not self.indexed:
                    raise TypeError("'%s' is not indexed" % (self.__propname,))
                try:
                    index = self.__index
                except:
                    index_name = "%s %s %s" % (
                        self.__class._meta.app_label,
                        self.__class.__name__,
                        self.__propname,)
                    self.__index = index = DjangoNeo.index(index_name)
                return index

            def get_default(self):
                return self.__property.default

            def __cmp__(self, other):
                return cmp(self.creation_counter, other.creation_counter)

            @staticmethod
            def __values_of(instance, create=True):
                try:
                    values = instance.__values
                except:
                    values = {}
                    if create:
                        instance.__values = values
                return values

            @staticmethod
            def __properties_for(obj_or_cls):
                meta = obj_or_cls._meta
                try:
                    properties = meta.__properties
                except:
                    meta.__properties = properties = {}
                return properties
            
            def _save_(instance, node):
                values = BoundProperty.__values_of(instance)
                if values:
                    properties = BoundProperty.__properties_for(instance)
                    for key, value in values.items():
                        self = properties[key]
                        old, value = self.__set_value(instance, value)
                        if self.indexed:
                            if self.unique and value is not None:
                                old_node = self.index[value]
                                if old_node and old_node != node:
                                    raise ValueError(
                                        "Duplicate index entries for <%s>.%s" %
                                        (instance.__class__.__name__,
                                         self.name))
                            if old is not None:
                                self.index.remove(old, node)
                            if value is not None:
                                self.index.add(value, node)
                    values.clear()
            NodeModel._save_neo4j_Properties = staticmethod(_save_)
            del _save_

            def __get__(self, instance, cls=None):
                if instance is None: return self
                values = self.__values_of(instance, create=False)
                if self.__propname in values:
                    return values[self.__propname]
                else:
                    return self.__get_value(instance)

            def __set__(self, instance, value):
                if write_through(instance):
                    self.___set_value(instance, value)
                else:
                    values = self.__values_of(instance)
                    values[self.__propname] = value

            @transactional
            def __get_value(self, instance):
                try:
                    node = instance._neo4j_underlying
                except: # no node existed
                    pass
                else:
                    try:
                        return self.__property.from_neo(node[self.__propname])
                    except: # no value set on node
                        pass
                return self.get_default() # fall through: default value
            @transactional
            def __set_value(self, instance, value):
                value = self.__property.to_neo(value)
                underlying = instance._neo4j_underlying
                try:
                    old = underlying[self.__propname]
                except:
                    old = None
                underlying[self.__propname] = value
                return old, value

        return Property
