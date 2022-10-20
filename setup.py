from setuptools import setup, find_packages


setup(
    name='camp_parser',
    version='0.1',
    license='MIT',
    author="HRNPH",
    author_email='hirunkul2548@gmail.com',
    packages=find_packages('camp_parser'),
    package_dir={'': 'camp_parser'},
    url='https://github.com/HRNPH/Camphub_api_unofficial',
    keywords='camp_parser',
    install_requires=[
          'requests',
            'bs4',
      ],

)