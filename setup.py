from setuptools import setup, find_packages
import os

version = '1.0.8.dev0'

setup(name='collective.dynapage',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
      open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Framework :: Plone :: 4.1",
          "Framework :: Plone :: 4.2",
          "Framework :: Plone :: 4.3",
      ],
      keywords='',
      author='Jukka Ojaniemi',
      author_email='jukka.ojaniemi@gmail.com',
      url='https://github.com/pingviini/collective.dynapage',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['collective'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Products.CMFPlone',
          'plone.app.dexterity[grok,relations]',
          'plone.behavior',
          'plone.app.referenceablebehavior',
          'plone.app.uuid',
          'plone.namedfile[blobs]',
          'collective.js.doubletap',
          # -*- Extra requirements: -*-
      ],
      extras_require={
          'test': ['plone.app.testing', ]
      },
      entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
