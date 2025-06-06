# Usage of __all__ in Python

The __all__ variable is a list of names that defines what gets imported when using from module import *. It controls what is exposed as the public API of a module or package.

## 1. How __all__ Works

Consider the following example:

# mymodule.py
var1 = "Hello"
var2 = "World"

def func1():
    return "Function 1"

def func2():
    return "Function 2"

__all__ = ["var1", "func1"]  # Only these will be imported with '*'

Now, if another module does:

from mymodule import *
print(var1)   # ✅ Works
print(func1())  # ✅ Works
print(var2)   # ❌ NameError (not in __all__)
print(func2())  # ❌ NameError (not in __all__)

Without __all__, everything that does not start with _ would be imported.

## 2. __all__ in Packages (__init__.py)

In a package, __all__ specifies which submodules are imported when using from package import *.

# mypackage/__init__.py
from .module1 import foo
from .module2 import bar

__all__ = ["foo", "bar"]  # Only foo and bar will be exposed

So when someone does:

from mypackage import *

Only foo and bar will be available.

## 3. __all__ in Model Imports

When centralizing model imports, __all__ ensures only specific models are imported when using from models.__all_models import *.

# models/__all_models.py
from .user import User
from .product import Product

__all__ = ["User", "Product"]

Now:

from models.__all_models import *
print(User)  # ✅ Works
print(Product)  # ✅ Works

If Order was in models/order.py but not in __all__, it wouldn’t be imported.

## 4. When Should You Use __all__?

✅ Use it if you want to control what gets exposed when doing import *.
✅ Use it to enforce API boundaries in libraries.
❌ Avoid it in normal scripts where explicit imports (import foo) are better.
TL;DR

    __all__ controls what gets imported with from module import *.
    It helps define a public API in libraries and packages.
    It’s not required for normal imports (import module).

