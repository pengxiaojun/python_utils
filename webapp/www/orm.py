# -*-coding: utf-8 -*-


import asyncio
import aiomysql
import logging


def log(sql, args=()):
    logging.info(sql)


@asyncio.coroutine
def create_pool(loop, **kw):
    logging.info("create database connection pool...")
    global __pool
    __pool  = yield from aiomysql.create_pool(
        host = kw.get('host', 'localhost'),
        port = kw.get('port', 3306),
        user = kw['user'],
        password = kw.get('password', 'password'),
        db = kw['database'],
        charset = kw.get('charset', 'utf8'),
        autocommit = kw.get('autocommit', True),
        maxsize = kw.get('maxsize', 10),
        minsize = kw.get('minsize', 1),
        loop = loop
    )


@asyncio.coroutine
def select(sql, args, size=None):
    log(sql)
    global __pool
    with(yield from __pool) as conn:
        cursor = yield from conn.cursor(aiomysql.DictCursor)
        yield from cursor.execute(sql.replace('?', '%s'), args or ())
        if size:
            rs = yield from cursor.fetchmany(size)
        else:
            rs = yield from cursor.fetchall()
        yield from cursor.close()
        logging.info('rows returned:%s' % len(rs))
        return rs


@asyncio.coroutine
def execute(sql, args, autocommit=True):
    log(sql)
    with (yield from __pool) as conn:
        if not autocommit:
            yield from conn.begin()
        try:
            cursor = yield from conn.cursor()
            yield from cursor.execute(sql.replace('?', '%s'), args or ())
            affected = cursor.rowcount
            yield from cursor.close()
            if not autocommit:
                yield from conn.commit()
        except BaseException as e:
            if not autocommit:
                yield from conn.rollback()
            raise
        return affected


def create_args_string(num):
    L = []
    for i in range(num):
        L.append('?')
    return ','.join(L)


class Field(object):
    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def str(self):
        return '<%s,%s:%s>' % (self.__class__.__name__,
                               self.name,
                               self.column_type)


class StringField(Field):
    def __init__(self,
                 name=None,
                 primary_key=False,
                 default=None,
                 ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):
    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):
    def __init__(self, name=None, primary_key=None, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):
    def __init__(self, name=None, primary_key=None, default=0.0):
        super().__init__(name, 'float', primary_key, default)


class TextField(Field):
    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        table_name = attrs.get('__table__', None) or name
        primary_key = None
        mappings = dict()
        fields = []

        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    if primary_key:
                        raise Exception('duplicate primary key %s' % k)
                    primary_key = k

                else:
                    fields.append(k)

        if not primary_key:
            raise Exception('Primary key not found')

        for k in mappings.keys():
            attrs.pop(k)

        escape_fields = list(map(lambda f:'`%s`' % f, fields))
        attrs['__mappings__'] = mappings
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['__select__'] = 'select `%s`,%s from `%s`' % (
            primary_key,
            ','.join(escape_fields),
            table_name)
        attrs['__insert__'] = 'insert into `%s`(%s, `%s`)values(%s)' % (
            table_name,
            ','.join(escape_fields),
            primary_key,
            create_args_string(len(escape_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (
            table_name,
            ','.join(map(lambda f:'`%s`=?' % (mappings.get(f).name or f) , fields)),
            primary_key)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % (
            table_name, primary_key)

        #print(attrs['__insert__'])
        #print(attrs['__update__'])
        #print(attrs['__delete__'])
        #print(attrs['__select__'])
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("'Model' object has no attribute %s" % key)

    def __setattr__(self, key, val):
        self[key] = val

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        val = self.getValue(key)
        if val is None:
            field = self.__mappings__[key]
            if field.default is not None:
                val = field.default() if callable(field.default) else field.default
                logging.info('using default for key %s=%s', key, str(val));
                setattr(self, key, val)
        return val

    @classmethod
    @asyncio.coroutine
    def findall(cls, where=None, args=None, **kw):
        ' find object by where caluse'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)

        if args is None:
            args = []

        orderBy = kw.get('orderby', None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)

        limit = kw.get('limit', None)
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit, tuple) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value:%s' % str(limit))

        rs = yield from select(' '.join(sql), args)
        print(rs)
        return [cls(**r) for r in rs]


    @classmethod
    @asyncio.coroutine
    def findnumber(cls, selectField, where=None, args=None):
        'find number by where'
        sql = ['select %s _num_ from `%s`' % (selectField, cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)

        rs = yield from select(' '.join(sql), args, 1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']

    @classmethod
    @asyncio.coroutine
    def find(cls, pk):
        'find object by primary key'
        rs = yield from select('%s where `%s`=?' % (cls.__select__,
                                                    cls.__primary_key__),[pk],1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @asyncio.coroutine
    def save(self):
        'save object to database'
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = yield from execute(self.__insert__, args)
        if (rows != 1):
            logging.warn('failed to insert record.affected row:%s' % rows)

    @asyncio.coroutine
    def update(self):
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = yield from execute(self.__update__, args)
        if (rows != 1):
            logging.warn('failed to update record.affected row:%s' % rows)

    @asyncio.coroutine
    def remove(self):
        'remove object by primary key'
        args = [self.getValue(self.__primary_key__)]
        rows = yield from execute(self.__delete__, args)
        if (rows != 1):
            logging.warn('failed to remove recor.affected row:%s' % rows)
