# -*-coding: utf-8 -*-


# using metaclass in python implement a simple orm prototype


class Field(object):

    def __init__(self, name, column_type):
        self.name = name
        self.column_type = column_type

    def __str__(self):
        return "<%s:%s>" % (self.name, self.column_type)


class IntegerField(Field):

    def __init__(self, name):
        super(IntegerField, self).__init__(name, 'bigint')


class StringField(Field):

    def __init__(self, name):
        super(StringField, self).__init__(name, 'varchar(100)')


class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        # skipping Model class
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        print('Found model: %s' % name)
        mappings = dict()
        for k, v in attrs.items():
            if (isinstance(v, Field)):
                print('Found mapping: %s -> %s' % (k, v))
                mappings[k] = v
        for k in mappings.keys():
            attrs.pop(k)

        # save to attribute
        attrs['__mappings__'] = mappings
        attrs['__table__'] = name

        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kv):
        super(Model, self).__init__(**kv)


    def __getattr__(self, key):
        try:
            return self[key]
        except:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)


    def __setattr__(self, key, val):
        self[key] = val


    def save(self):
        fields = []
        params = []
        args = []

        for k, v in self.__mappings__.items():
            fields.append(v.name)
            params.append('?')
            args.append(getattr(self, k, None))

        sql = 'insert into %s (%s)values(%s)' % (self.__table__,
                                                 ','.join(fields),
                                                 ','.join(params))

        print('Sql => %s' % sql)
        print('args => %s' % str(args))


class User(Model):
    id = IntegerField("id")
    name = StringField("name")
    email = StringField("email")
    pasword = StringField("password")


u = User(id="1", name="bob", email="bob@gmail.com", password="password")
u.save()
