shell_sources = [
  '__init__.py',
  '__main__.py'
  ]
constants_sources = [
  'constants/Browser.py',
  'constants/__init__.py',
  'constants/Os.py',  
  'constants/Version.py'
  ]
gui_sources = [
  'gui/__init__.py',
  'gui/about_ui.py',
  'gui/addlink_ui.py',
  'gui/addmagnet_ui.py',
  'gui/addtorrent_ui.py',
  'gui/after_download_ui.py',
  'gui/customized_widgets.py',
  'gui/get_magnet_link_ui.py',
  'gui/log_window_ui.py',
  'gui/mainwindow_ui.py',
  'gui/progress_ui.py',
  'gui/properties_ui.py',
  'gui/resources.py',
  'gui/setting_ui.py',
  'gui/text_queue_ui.py',
  'gui/torrent_progress_ui.py',
  'gui/video_finder_progress_ui.py'
  ]
scripts_sources = [
  'scripts/__init__.py',
  'scripts/about.py',
  'scripts/addlink.py',
  'scripts/addmagnet.py',
  'scripts/addtorrent.py',
  'scripts/after_download.py',
  'scripts/browser_integration.py',
  'scripts/browser_plugin_queue.py',
  'scripts/bubble.py',
  'scripts/check_proxy.py',
  'scripts/compatibility.py',
  'scripts/data_base.py',
  'scripts/download_link.py',
  'scripts/error_window.py',
  'scripts/initialization.py',
  'scripts/libtorrent_wrapper.py',
  'scripts/log_window.py',
  'scripts/logger.py',
  'scripts/mainwindow.py',
  'scripts/newopen.py',
  'scripts/osCommands.py',
  'scripts/persepolis.py',
  'scripts/persepolis_lib_prime.py',
  'scripts/play.py',
  'scripts/progress.py',
  'scripts/properties.py',
  'scripts/queue.py',
  'scripts/setting.py',
  'scripts/shutdown.py',
  'scripts/spider.py',
  'scripts/startup.py',
  'scripts/text_queue.py',
  'scripts/torrent_progress.py',
  'scripts/useful_tools.py',
  'scripts/video_finder.py',
  'scripts/video_finder_addlink.py',
  'scripts/video_finder_progress.py',
  'scripts/ytdlp_downloader.py'
  ]

python3.install_sources(shell_sources, subdir: 'persepolis')
python3.install_sources(gui_sources, subdir: join_paths('persepolis', 'gui'))
python3.install_sources(scripts_sources, subdir: join_paths('persepolis', 'scripts'))
python3.install_sources(constants_sources, subdir: join_paths('persepolis', 'constants'))

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('pythonsitepackagedir', python3.get_install_dir())

configure_file(
  input: 'persepolis.py',
  output: 'persepolis',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'r-xr-xr-x'
)
