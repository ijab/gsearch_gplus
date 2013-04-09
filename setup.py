from setuptools import setup

setup(name='CSE+', version='0.2',
      description='OpenShift Python-2.7 Community Cartridge based application',
      author='iJab', author_email='zhancaibao@gmail.com',
      url='http://www.python.org/sigs/distutils-sig/',

      #  Uncomment one or more lines below in the install_requires section
      #  for the specific client drivers/modules your application needs.
      install_requires=['greenlet', 'gevent',
                        #  'MySQL-python',
                          'pymongo',
                        #  'psycopg2',
      ],
     )
