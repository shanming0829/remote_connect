import yaml


class Config(object):
    def __init__(self, config_file):
        self.config_file = config_file

        self._parse_config()

    def _parse_config(self):
        with open(self.config_file) as f:
            self.data = yaml.load(f)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        raise AttributeError("No attribute {}".format(str(item)))


if __name__ == '__main__':
    import os

    '../nightly_statistic.yaml'
    config = Config(os.path.join(os.getcwd(), '../../nightly_statistic.yaml'))
    import pprint

    pprint.pprint(config.job)
