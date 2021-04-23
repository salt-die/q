NO_DEFAULT = type('', (), {'__repr__': lambda self: 'NO_DEFAULT'})()  # This sentinal object identifies fields with no default values;
                                                                      # it has a slightly more useful repr than `object()`.
RESERVED = _, FIELDS = '__attrs__', '__fields__'  # These are used to demarcate class attributes from default field values in the class body

def reorder(fields):
    """
    Reorder the fields so that fields with no default values come first.
    Order between non-default value fields and default value fields is maintained otherwise.
    """
    no_defaults = {field: default for field, default in fields.items() if default is NO_DEFAULT}
    defaults = {field: default for field, default in fields.items() if default is not NO_DEFAULT}
    return no_defaults | defaults

def init_source(fields):
    """Returns the source for a default __init__
    """
    args = ', '.join(field if default is NO_DEFAULT else f'{field}={default!r}' for field, default in fields.items())
    body = '\n'.join(f'    self.{field} = {field}' for field in fields)
    return f'def __init__(self, {args}):\n{body}'

def repr_source(fields):
    """Returns the source for a default __repr__
    """
    attrs = ', '.join(f'{field}={{self.{field}!r}}' for field in fields)
    return f'def __repr__(self):\n    return f"{{type(self).__name__}}({attrs})"'

def is_dunder(method):
    return method.startswith('__') and method.endswith('__')


class _q_namespace(dict):
    def __init__(self, context):
        super().__init__()
        self.fields = {}
        self.__context = context or {}
        self.__collecting_fields = True

    def __setitem__(self, key, value):
        if self.__collecting_fields and not is_dunder(key):
            self.fields[key] = value
        else:
            super().__setitem__(key, value)

    def __missing__(self, key):
        if key in RESERVED:
            self.__collecting_fields = key == FIELDS
            return

        if is_dunder(key):  # We allow python to add dunder methods by raising a KeyError.
                            # Consequently, fields can't be dunder-ed.
            raise KeyError(key)

        if key in self.__context:
            return self.__context[key]

        if self.__collecting_fields:
            self[key] = NO_DEFAULT
            return NO_DEFAULT

        raise SyntaxError(f'class attribute `{key}` must be assigned some value')


class qMeta(type):
    def __prepare__(name, bases, context=None):
        return _q_namespace(context)

    def __new__(meta, name, bases, namespace, context=None):
        fields = { }
        for base in reversed(bases):
            fields |= getattr(base, '__fields__', { })
        fields |= namespace.fields
        namespace['__fields__'] = fields = reorder(fields)

        if fields and '__init__' not in namespace:
            exec(init_source(fields), globals(), namespace)

        if '__repr__' not in namespace:
            exec(repr_source(fields), globals(), namespace)

        # Add additional default methods as needed!

        return super().__new__(meta, name, bases, namespace)


class q(metaclass=qMeta):
    pass
