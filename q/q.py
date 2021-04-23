NO_DEFAULT = type('', (), {'__repr__': lambda self: 'NO_DEFAULT'})()  # This sentinal object identifies fields with no default values;
                                                                      # it has a slightly more useful repr than `object()`.
CLASS_ATTRS, FIELDS = '__attrs__', '__fields__'  # These are used to demarcate class attributes from default field values in the class body

def separate(fields):
    """Separate keys with no default values from keys with default values.
    """
    no_defaults = []
    defaults = {}
    for key, value in fields.items():
        if value is NO_DEFAULT:
            no_defaults.append(key)
        else:
            defaults[key] = value
    return no_defaults, defaults


class AutoDict(dict):
    def __init__(self, context):
        super().__init__( __fields={} )  # Treating `__fields` as an ordered-set, i.e., its values are irrelevant
        self.__context = context or {}
        self.__add_to = FIELDS

    def __setitem__(self, key, value):
        if self.__add_to == FIELDS and not ( key.startswith('__') and key.endswith('__') ):
            self['__fields'][key] = value
        else:
            super().__setitem__(key, value)

    def __missing__(self, key):
        if key in (CLASS_ATTRS, FIELDS):
            self.__add_to = key
        elif key.startswith('__') and key.endswith('__'):
            raise KeyError(key)
        elif key in self.__context:
            return self.__context[key]
        elif self.__add_to == FIELDS:
            self[key] = NO_DEFAULT
        else:
            raise SyntaxError(f'class attribute `{key}` must be assigned some value')


class qMeta(type):
    def __prepare__(name, bases, context=None):
        return AutoDict(context)

    def __new__(meta, name, bases, namespace, context=None):
        namespace['__fields__'] = attrs = {}
        for base in bases:
            attrs |= getattr(base, '__fields__', {})
        attrs |= namespace['__fields']  # __fields != __fields__
        del namespace['__fields']

        no_defaults, defaults = separate(attrs)
        all_args = no_defaults + list(defaults)

        if attrs and '__init__' not in namespace:
            positional_args = ', '.join(no_defaults)
            default_args = ', '.join(f'{arg}={val!r}' for arg, val in defaults.items())
            init_header = f'def __init__(self, {(positional_args + ", ") if no_defaults else ""}{default_args}):\n'
            init_body = '\n'.join(f'    self.{attr}={attr}' for attr in all_args)
            exec(init_header + init_body, globals(), namespace)

        if '__repr__' not in namespace:
            args = ', '.join(f'{attr}={{self.{attr}!r}}' for attr in all_args)
            repr_ = f'def __repr__(self):\n    return f"{name}({args})"'
            exec(repr_, globals(), namespace)

        return super().__new__(meta, name, bases, namespace)


class q(metaclass=qMeta):
    pass
