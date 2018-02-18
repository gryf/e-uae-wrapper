=============
E-UAE Wrapper
=============

This utility is a wrapper on old E-UAE_ emulator, to help divide configuration
to common and specific per ``.uaerc`` configuration, and combine them together
during runtime.


Requirements
============

- Python (2 or 3)
- `e-uae`_

e-uae-wrapper supports several types of archives:

- `7z`_
- `lha`_
- `lzx`_ - decompress only
- `rar`_ - if only ``unrar`` is available, than only decompression is supported
- `tar`_, also compressed with:

  - bzip2
  - gzip
  - xz

- `zip`_

All of those formats should have corresponding software available in the
system, otherwise archive extraction/compression will fail.


Configuration
=============

Optional, global (a common) config file will be searched on
``XDG_CONFIG_HOME/e-uae.ini``, (usually at ``~/.config/e-uae.ini`` and supports
anthing, which could be used for templating, ie paths to roms, floppies,
harddrives etc. Anything which might be treated as a common variables for all
avalialbel ``.uaerc`` configs.  For example:

.. code:: ini

   [config]
   wrapper_kickstart_path = /home/user/Amiga/kickstart

and with corresponding e-uae configuration (i.e. ``.uaerc``), it can be used
like:

.. code::

   config_description=UAE default configuration
   config_hardware=false
   config_host=false
   config_version=0.8.29
   ...
   kickstart_rom_file={{wrapper_kickstart_path}}/kick.rom

Note, that such options should always start with ``wrapper`` word, and in
``.uaerc`` has to be enclosed with curly braces, like in the example above.

There are two additional build-in options which can be used in templates:

* ``wrapper_tmp_path`` - which points to the path, where ``.uaerc`` is
  generated, and potentially archives are extracted
* ``wrapper_config_path`` - which point to the absolute path, where passed by
  the commandline  configuration (``.uaerc``) is placed.

All wrapper options which name contain *path* word will be treatead as paths,
and as a consequence will be replaced with full path to the item, for example:

.. code::

   wrapper_foo_path=/some/filepath
   filesystem=rw,HD:{{wrapper_foo_path}}../otherpath/hd

will become:

.. code::

   filesystem=rw,HD:/some/otherpath/hd

Note, that using templates like ``{{wrapper_foo_path}}/otherpath/hd`` will
create path ``/otherpath/hd`` instead of ``/some/filepath/otherpath/hd``
because of how ``os.path.join`` work. Be careful on using ``/`` in paths.


Installation
============

It's alfa stage of the development, so that it is not easy way to do the
installation yet. However, to use it, it's enough to clone this repository,
copy ``scripts/e-uae-wrapper`` to sowhere in the ``PATH`` and point
``PYTHONPATH`` to ``e_uae_wrapper``, like:

.. code:: shell-session

   $ git clone https://github.com/gryf/e-uae-wrapper
   $ mkdir ~/bin
   $ export PATH=$PATH:$HOME/bin
   $ export PYTHONPATH=$PYTHONPATH:$(pwd)/e-uae-wrapper


Usage
=====

The usage is simple. Prepare some ``.uaerc`` file as described above, use
command ``e-uae-wrapper`` with configuration passed as an argument:

.. code:: shell-session

   $ e-uae-wrapper uaerc-config-file


Modules
=======

There are following modules currently implemented:

- plain
- archive

Plain
-----

This module is simply for running emulator with template usage. It makes easy
to put relative paths in ``.uaerc`` configuration.

Options used:

* None

archive
-------

This module is quite useful in two use cases. First is a usual work with
Workbench, where there is a need to keep changes of filesystem. Second is the
opposite - if there is a need to test some software, but not necessary keep it
in a Workbench, than it will act as a temporary copy of the system, so that
next time e-uae will be run, there will be no files of tested software
cluttering around.

Options used:

* ``wrapper`` (required) with ``archive`` as an value
* ``wrapper_archive`` (required) path to the archive with assets (usually means
  whole system directories, floppies or hard disk images)
* ``wrapper_gui_msg`` (optional) if set to "1", will display a graphical
  message during extracting files
* ``wrapper_persist_data`` (optional) if set to "1", will compress (possibly
  changed) data, replacing original archive

Example configuration:

.. code::

   config_description=UAE default configuration
   wrapper=archive
   wrapper_archive=Workbench_3.1.tar.bz2
   wrapper_archiver=lha
   wrapper_gui_msg=1
   wrapper_persist_data=1
   # ...

And execution is as usual:

.. code:: shell-session

   $ e-uae-wrapper Workbench.fs-uae

This module will do several steps:

- create temporary directory
- extract provided in configuration archive
- copy configuration under name ``.uaerc``
- run the e-uae emulator
- optionally create new archive under the same name as the original one and
  replace it with original one.

License
=======

This work is licensed on 3-clause BSD license. See LICENSE file for details.

.. _e-uae: http://www.rcdrummond.net/uae/
.. _relative configuration file: https://fs-uae.net/configuration-files
.. _rar: http://www.rarlab.com/rar_add.htm
.. _7z: http://p7zip.sourceforge.net/
.. _lha: http://lha.sourceforge.jp
.. _lzx: http://aminet.net/package/misc/unix/unlzx.c.readme
.. _tar: https://www.gnu.org/software/tar/
.. _zip: http://www.info-zip.org
.. _CheeseShop: https://pypi.python.org/pypi/fs-/fs-uae-wrapperuae-wrapper
