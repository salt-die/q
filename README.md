`q` for `q`uick class definitions!  More magical and less overhead than dataclasses or attrs:

```py
>>> from q import q
>>> class Point(q):
...     x, y
...
>>> Point(1, 2)
Point(x=1, y=2)
```
This is all one needs to get the `__init__` and `__repr__` one expects.

One can even define default values:
```py
>>> class Point(q):
...     x, y
...     z = 1
...
>>> Point(1, 2)
Point(x=1, y=2, z=1)
```

To specify class attributes and default values:
```py
>>> class Point(q):
...     __attrs__
...     metric = "euclidean"
...     __fields__
...     x, y
...     z = 1
...
>>> Point(1, 2)
Point(x=1, y=2, z=1)
>>> Point.metric
'euclidean'
```

`q` assumes everything is a field until told otherwise, so one can re-order above to the equivalent definition:
```py
>>> class Point(q):
...     x, y
...     z = 1
...     __attrs__
...     metric = "euclidean"
```

Typically, names not found in the class' namespace would be added as a field with no default value. This can create some surprising behavior:
```py
>>> default_z = 100
>>> class Point(q):
...     x, y
...     z = default_z
...
>>> Point(1, 2)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: __init__() missing 2 required positional arguments: 'default_z' and 'z'
```

We can remedy this by providing a context:
```py
>>> default_z = 100
>>> class Point(q, context=globals()):
...     x, y
...     z = default_z
...
>>> Point(1, 2)
Point(x=1, y=2, z=100)
```