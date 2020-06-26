# -*- coding: utf-8 -*-
"""
Created on Fri Jun 26 14:23:46 2020

@author: Asja
"""

**Bibliorecordsminer**

Bibliorecordsminer is a Python library for publications lists mining.

**Installation**

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install bibliorecordsminer.

```bash
pip install bibliorecordsminer
```

**Usage**

```python
import bibliorecordsminer as brm

# extracts text from pdf files in 'path'-folder ans save it in folder 
#  xlsx. create list with names of failed pdfs
brm.extract_and_split(path)

# Filter non-bibliographic records, extract years of publications, extract 
# types of publications (headers in publications lists)
brm.filtration(path, x)

```
**Contributing**
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

**License**
[MIT](https://choosealicense.com/licenses/mit/)