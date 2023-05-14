import configparser
import pathlib

_conf = None


def get_conf(name):
    global _conf
    if _conf is None:
        _conf = configparser.ConfigParser()
        _conf.read(pathlib.Path(__file__).parent.parent / "config.ini")
    return _conf["DEFAULT"][name]
