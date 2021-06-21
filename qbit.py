import qbittorrentapi
import logging
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read('config.ini')
HOST = CONFIG['qbittorrent']['host']
PORT = int(CONFIG['qbittorrent']['port'])
USERNAME = CONFIG['qbittorrent']['username']

CLIENT = qbittorrentapi.Client(host=HOST, port=PORT, username=USERNAME)
LOGGER = logging.getLogger('qbittorrent')
_consoleHandler = logging.StreamHandler()
_consoleHandler.setLevel(logging.INFO)
LOGGER.addHandler(_consoleHandler)
LOGGER.info(f'qBittorrent: {CLIENT.app.version}')