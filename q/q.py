NO_DEFAULT = type('', (), {'__repr__': lambda self: 'NO_DEFAULT'})()  # This sentinal object identifies fields with no default values;
                                                                      # it has a slightly more useful repr than `object()`.
RESERVED = _, FIELDS = '__attrs__', '__fields__'  # These are used to demarcate class attributes from default field values in the class body

def separate(fields):
    """Separate fields with no default values from fields with default values.
    """
    no_defaults = []
    defaults = {}
    for field, default in fields.items():
        if default is NO_DEFAULT:
            no_defaults.append(field)
        else:
            defaults[field] = default
    return no_defaults, defaults

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
        namespace['__fields__'] = fields = {}
        for base in reversed(bases):
            fields |= getattr(base, '__fields__', {})
        fields |= namespace.fields

        no_defaults, defaults = separate(fields)
        all_args = no_defaults + list(defaults)

        # Default __init__
        if fields and '__init__' not in namespace:
            positional_args = ', '.join(no_defaults)
            default_args = ', '.join(f'{arg}={val!r}' for arg, val in defaults.items())
            init_header = f'def __init__(self, {(positional_args + ", ") if no_defaults else ""}{default_args}):\n'
            init_body = '\n'.join(f'    self.{attr}={attr}' for attr in all_args)
            exec(init_header + init_body, globals(), namespace)

        # Default __repr__
        if '__repr__' not in namespace:
            args = ', '.join(f'{attr}={{self.{attr}!r}}' for attr in all_args)
            repr_ = f'def __repr__(self):\n    return f"{name}({args})"'
            exec(repr_, globals(), namespace)

        # We encourage you to add your own default methods as needed.  This code is short enough to be easily maintainable by you!
        # Copy it to your project and hack away!
        return super().__new__(meta, name, bases, namespace)


class q(metaclass=qMeta):
    pass
