from distutils.core import setup

setup(name='BetterXML',
      version='1.0',
      description='BetterXML Python Distribution',
      url='http://www.betterxml.org/',
      package_dir = {'':'src'},
      packages = ['bxml', 'bxml.util', 'bxml.nxml', 'bxml.xelement1', 'bxml.xelement2',
                  'bxml.shell', 'bxml.xir']
     )

