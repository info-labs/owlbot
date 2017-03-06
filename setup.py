from owlbot.metadata import __version__, __description__, __license__

try:
    from distutils.core import setup, find_packages
except ImportError:
    from setuptools import setup, find_packages

setup(
    name="owlbot",
    version=__version__,
    description=__description__,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Natural Language :: Japanese',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System :: Archiving',
    ],
    keywords='warc archive',
    maintainer='mugwort_rc',
    maintainer_email='mugwort.rc@gmail.com',
    url='https://github.com/info-labs/owlbot',
    download_url='https://github.com/info-labs/owlbot/tarball/v%s' % __version__,
    license=__license__,
    install_requires=[
        "warc",
        "requests",
        "dnspython",
        "lxml",
    ],
    include_package_data=True,
    packages=find_packages(),
    zip_safe=False,
)
