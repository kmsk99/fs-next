Introduction
============

PyFilesystem is a Python module that provides a common interface to any
filesystem.

Think of PyFilesystem ``FS`` objects as the next logical step to
Python's ``file`` objects. In the same way that file objects abstract a
single file, FS objects abstract an entire filesystem.


Installing
----------

FS Next is an independent maintenance fork of PyFilesystem2. Install it in a
fresh Python 3.10+ virtual environment::

    python -m pip install fs-next==0.1.0

Imports remain ``import fs``. Do not install ``fs`` and ``fs-next`` together:
they provide the same package files. Dependencies declared on the distribution
``fs`` must be migrated to ``fs-next``; its different name cannot satisfy them.
See the `migration guide <https://github.com/kmsk99/fs-next/blob/main/docs/migration.md>`_
and `support policy <https://github.com/kmsk99/fs-next/blob/main/docs/support-policy.md>`_.

The maintained source is at `kmsk99/fs-next <https://github.com/kmsk99/fs-next>`_.
The original source, history and MIT notices are preserved from
`PyFilesystem2 <https://github.com/PyFilesystem/pyfilesystem2>`_. No FS Next conda
package is currently published by this project.
