try:
    import configparser as  ConfigParser
except:
    import ConfigParser
import os
path = '../conf/app_lbs.conf'
# path = 'app.conf'

def getConfig(section, key):
    config = ConfigParser.ConfigParser()
    #/home/epro/proepro/conf
    env=os.getenv('HOME')
    # print "the env is",env
    # path = './cps.conf'
    # path=str(env)+'/proepro/conf/cps.conf'
    config.read(path)
    return config.get(section, key)

if __name__ == '__main__':
    print 
    # print dir(os)
    #main()