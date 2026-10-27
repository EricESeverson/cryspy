# cryspy

<!-- Eric: your description of the library goes here. -->

## Using it in Colab

Run this cell. Running it again pulls the newest version.

```python
!git clone -q https://github.com/EricESeverson/cryspy.git /content/cryspy 2>/dev/null || git -C /content/cryspy pull -q
import sys, importlib
sys.path.insert(0, "/content/cryspy")
import cryspy; importlib.reload(cryspy)
print(cryspy.__version__)
```
