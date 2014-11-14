****************************
Mopidy-ALCD
****************************

.. image:: https://img.shields.io/pypi/v/Mopidy-ALCD.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-ALCD/
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/Mopidy-ALCD.svg?style=flat
    :target: https://pypi.python.org/pypi/Mopidy-ALCD/
    :alt: Number of PyPI downloads

.. image:: https://img.shields.io/travis/NuAoA/mopidy-ALCD/master.png?style=flat
    :target: https://travis-ci.org/NuAoA/mopidy-ALCD
    :alt: Travis CI build status

.. image:: https://img.shields.io/coveralls/NuAoA/mopidy-ALCD/master.svg?style=flat
   :target: https://coveralls.io/r/NuAoA/mopidy-ALCD?branch=master
   :alt: Test coverage

A mopidy frontend for Adafruits 16x2 5 button LCD Pi Plate display. It has some basic support for library/playlist browsing.


Installation
============
open download directory and run:

    python setup.py install 

Also, you need to install the netifaces package, run:

    easy_install netifaces

Finally, you need to have setup the Adafruit LCD as outlined in this tutorial:

https://learn.adafruit.com/adafruit-16x2-character-lcd-plus-keypad-for-raspberry-pi/usage
	
	
Configuration
=============

I set this up for my White/Blue LCD display, so if your blacklight doesn't turn on or the colors are off, edit Adafruit_LCD_plate.py

Useage
=============

Select: opens menus/up a menu (left and right select option)

Left: Play/pause

Right: Next track

up/down: Volume control


Project resources
=================

- `Source code <https://github.com/NuAoA/mopidy-alcd>`_
- `Issue tracker <https://github.com/NuAoA/mopidy-alcd/issues>`_
- `Development branch tarball <https://github.com/NuAoA/mopidy-alcd/archive/master.tar.gz#egg=Mopidy-ALCD-dev>`_


Changelog
=========

v0.1.0 (RELEASE)
----------------------------------------

- Initial release.