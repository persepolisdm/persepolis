desktop_file='com.github.persepolisdm.persepolis.desktop'
xml_file='com.github.persepolisdm.persepolis.appdata.xml'

conf = configuration_data()
conf.set('persepolisbin', join_paths(bindir, 'persepolis'))


configure_file(
  input: 'com.github.persepolisdm.persepolis.desktop.in',
  output: 'com.github.persepolisdm.persepolis.desktop',
  configuration: conf,
  install: true,
  install_dir: desktopdir,
)

install_data(xml_file, install_dir: appdatadir)

