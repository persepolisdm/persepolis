project('persepolis',
  version: '5.2.0', 
  meson_version: '>=0.61.2')

python = import('python')
python3 = python.find_installation('python3')

if not python3.found()
    error('No valid python3 installation found!')
endif

# run dependency check script
meson.add_install_script('check_dependencies.py')

prefix = get_option('prefix')
bindir = join_paths(prefix, get_option('bindir'))
datadir = join_paths(prefix, get_option('datadir'))
pythondir = join_paths(prefix, python3.get_path('purelib'))
pkgdatadir = join_paths(datadir, meson.project_name())
pkgappid = 'com.github.persepolisdm.persepolis'

appdatadir = join_paths(datadir, 'metainfo')
desktopdir = join_paths(datadir, 'applications')
persepolisdir = python3.get_install_dir(subdir: 'persepolis')
icondir = join_paths(datadir, 'icons', 'hicolor', 'scalable', 'apps')


subdir('persepolis')
subdir('man')
subdir('xdg')
subdir('resources')

