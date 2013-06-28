#! /usr/bin/env python

from distutils.core import setup


packages = ['djazz']

setup(name='Djazz',
      version='0.1',
      description='Django extension',
      author='Guillaume Dugas',
      author_email='dugas.guillaume@gmail.com',
      url='http://github.com/djazzproject/djazz',
      packages=packages,
      classifiers=[
          "Development Status :: 1 - Planning",
          "Framework :: Django",
          "Intended Audience :: Developers"
      ]
)
