from distutils.core import setup

setup(
  name = 'persepolis',
  packages = ['persepolis'], # this must be the same as the name above
  version = '2.3.3',
  description = 'Persepolis Download Manager',
  author = 'AliReza AmirSamimi, Sadegh Alirezaie',
  author_email = 'sadegh@webgo.ir',
  url = 'https://github.com/persepolisdm/persepolis', # use the URL to the github repo
  download_url = 'https://github.com/persepolisdm/persepolis', # I'll explain this in a second
  keywords = ['DownloadManager', 'aria2', 'Download'], # arbitrary keywords
  classifiers = [],
  install_requires=['PyQt5', 'requests'],
)

import install
