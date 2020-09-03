import configparser

class ConfigManager(object):
    def __init__(self, file_name="config.ini"):
        self.config = configparser.ConfigParser()
        self.file_name = file_name

    # display in console ini file content
    def display_config(self):
        print("Config:")
        for section in self.config.sections():
            print("Section: %s" % section)
            for options in self.config.options(section):
                print("%s\t%s\t%s"% (options, self.config.get(section, options), str(type(options))))

    # write to ini file
    def write(self):
        with open(self.file_name, 'w') as configfile:
            self.config.write(configfile)

    # read from ini file
    def read(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    # write to file default values
    def write_default(self):
        self.config['RECENT_IMAGES'] = {"first": "none", "second": "none", "third": "none", "fourth": "none", "fifth": "none"}
        self.config['OPTIONS'] = {'fullScreen': 'False', 'blockWindowSize': 'False'}
        with open(self.file_name, 'w') as configfile:
            self.config.write(configfile)

    # methods to get current options, first read file!
    def get_fullscreen(self):
        if self.config.has_option('OPTIONS', 'fullScreen') :
            val = self.config.get('OPTIONS', 'fullScreen')
            if val == 'False':
                return False
            else:
                return True

    def get_blocksize(self):
        if self.config.has_option('OPTIONS', 'blockWindowSize'):
            val = self.config.get('OPTIONS', 'blockWindowSize')
            if val == 'False':
                return False
            else:
                return True

    # methods for writing content
    # OPTIONS section
    def change_options(self, fullscreen, block_size):
        if fullscreen:
            self.config['OPTIONS']['fullScreen'] = 'True'
        else:
            self.config['OPTIONS']['fullScreen'] = 'False'
        if block_size:
            self.config['OPTIONS']['blockWindowSize'] = 'True'
        else:
            self.config['OPTIONS']['blockWindowSize'] = 'False'
        self.write()

    # RECENT_IMAGES section
    def add_recent(self, new_path):
        # how many shifts will be done
        step = 4
        # if new is current first then there are no changes
        if new_path != self.config['RECENT_IMAGES']['first']:
            # if new is current second there will be only one shift
            if new_path == self.config['RECENT_IMAGES']['second']:
                step = 1
            # if new is current third there will be two shifts
            elif new_path == self.config['RECENT_IMAGES']['third']:
                step = 2
            # if new is current fourth there will be three shifts
            elif new_path == self.config['RECENT_IMAGES']['fourth']:
                step = 3
            # if new is current fifth there will be four shifts
            elif new_path == self.config['RECENT_IMAGES']['fifth']:
                step = 4
            # chang first element and remember second for first shift
            temp_path = self.config['RECENT_IMAGES']['first']
            self.config['RECENT_IMAGES']['first'] = new_path
            # number of shifts is decreased after remember element to shift
            step -= 1
            # if there are more shifts
            if step != 0:
                temp_path2 = self.config['RECENT_IMAGES']['second']
                self.config['RECENT_IMAGES']['second'] = temp_path
                # number of shifts is decreased after remember element to shift
                step -= 1
                if step != 0:
                    temp_path = self.config['RECENT_IMAGES']['third']
                    self.config['RECENT_IMAGES']['third'] = temp_path2
                    # number of shifts is decreased after remember element to shift
                    step -= 1
                    if step != 0:
                        temp_path2 = self.config['RECENT_IMAGES']['fourth']
                        self.config['RECENT_IMAGES']['fourth'] = temp_path
                        self.config['RECENT_IMAGES']['fifth'] = temp_path2
                    else:
                        self.config['RECENT_IMAGES']['fourth'] = temp_path
                else:
                    self.config['RECENT_IMAGES']['third'] = temp_path2
            # if there are no more shifts - end
            else:
                self.config['RECENT_IMAGES']['second'] = temp_path
        self.write()

