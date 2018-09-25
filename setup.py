from setuptools import setup
from setuptools import find_packages

setup(
    name='synscer',
    version='0.0.1',
    url='https://github.com/donedeal-giorgio/postgresql_to_es_with_indexer',
    description="A POC for syncing data from postgresql into ES using a combination of PSQL events and indexer pattern",
    author="Giorgio Carta",
    author_email='giorgiocarta@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            # 'create_queue = psqltrigger.src.create_queue:main'
            'create_queue = create_queue:main',
            'listener = listener:main',
            'indexer = indexer:main',
        ]
    }
)
