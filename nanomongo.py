"""NanoMongo, a minimalistic python class to handle Mongo collections
"""
# import pymongo


class NanoMongo(dict):
    """
    NanonMongo class, subclass of dict

    B{TODO} auto private option for _* (more speed penality?)

    B{TODO} defaults forced for save? behaviors?
        eg: def save(self, *): self.lastupdate = now() && super().save

    @cvar collection: Collection to bind to
    @cvar _insert_defaults: values to set if not specificied for new records
    @cvar _private_fields items that should not be stored
    @cvar _safe_update default: wait for server reply when saving

    """
    collection = None
    _insert_defaults = None
    _private_fields = None
    _safe_updates = True

    @classmethod
    def find(cls, *args, **kwargs):
        kwargs['as_class'] = cls

        return cls.collection.find(*args, **kwargs)

    @classmethod
    def find_one(cls, *args, **kwargs):
        kwargs['as_class'] = cls

        return cls.collection.find_one(*args, **kwargs)

    def save(self, safe=None):
        if safe is None:
            safe = self._safe_updates

        if '_id' not in self and self._insert_defaults:
            for (key, value) in self._insert_defaults.iteritems():
                if key in self:
                    continue

                if callable(value):
                    self[key] = value(self)
                else:
                    self[key] = value

        # No private field, save as is
        if not self._private_fields:
            self._id = self.collection.save(self, safe=safe)
            return self._id

        copy = self.copy()
        for to_remove in set(self._private_fields) & set(copy):
            del copy[to_remove]
        self._id = self.collection.save(copy, safe=safe)
        return self._id

    def delete(self):
        return self.collection.remove(self['_id'])

    def reload(self):
        fresh = self.find_one(self._id)
        super(NanoMongo, self).update(fresh)
        for to_del in set(self) - set(fresh) - set(self._private_fields):
            del self[to_del]
        return self

    # strangelly, __getattr__ = __setitem__ won't work
    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        """Alias __getattr__ to __getitem___, but raise an Attribute error
        on miss (some libs rely on an AttributeError being raised)"""
        if name in self:
            return self[name]

        raise AttributeError("'%s' object has no attribute '%s'" %
                             (self.__class__.__name__, name))

# Override missing attributes to fetch dictionary items
NanoMongo.__delattr__ = NanoMongo.__delitem__
