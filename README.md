`q` for `q`uick class definitions!  More magical and less overhead than dataclasses or attrs:

```
In [1]: from q import q
In [2]: class Point(q):
   ...:     x, y
   ...:

In [3]: Point(1, 2)
Out[3]: Point(x=1, y=2)
```
This is all one needs to get the `__init__` and `__repr__` one expects.

One can even define default values:
```
In [4]: class Point(q):
   ...:     x, y
   ...:     z = 1
   ...:

In [5]: Point(1, 2)
Out[5]: Point(x=1, y=2, z=1)
```

To specify class attributes and default values:
```
In [6]: class Point(q):
   ...:     __attrs__
   ...:     metric = 'euclidean'
   ...:
   ...:     __fields__
   ...:     x, y
   ...:     z = 1
   ...:

In [7]: Point(1, 2)
Out[7]: Point(x=1, y=2, z=1)

In [8]: Point.metric
Out[8]: 'euclidean'
```

One can provide a context for the class to use names defined elsewhere (typically, names not found in the class' namespace would be added as a field with no default value):
```
In [9]: z = 100
   ...: class Point(q, context=globals()):
   ...:     __attrs__
   ...:     metric = 'euclidean'
   ...:
   ...:     __fields__
   ...:     x, y
   ...:     z = z
   ...:

In [9]: Point(1, 2)
Out[9]: Point(x=1, y=2, z=100)
```