#!/usr/bin/env python

from distutils.core import setup

setup(name="gheadset",
      description = "Python and GTK frontend for https://github.com/Sapd/HeadsetControl",
      author = "Joe Pfeiffer",
      author_email = "joseph@pfeifferfamily.net",
      version = "0.1.0",
      classifiers = [
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Development Status :: 4 - Beta ",
          "Environment :: X11 Applications :: GTK",
          "Programming Language :: Python :: 3",
          "Topic :: Utilities"
          ],

      install_requires = ["PyGObject"],
      packages = ["gheadset"],
      entry_points = {
          "gui_scripts" : [
              "gheadset = gheadset.__main__:main"
          ]
      },
)
      
