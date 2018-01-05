import six
from utils import tobinary,totext
class CpsAPIExceptions(Exception):
    ################error define 
    error_dict={
    '001':'the No of the Agent dupilicated ',
    '002':'the No of the Team dupilicated ',
    '003':'the No of the Tenant dupilicated ',
    'dup':'is dupilicated',
    }
    """docstring for CpsAPIExceptions"""
    def __init__(self, errorcode='default',errormsg=''):
        self.errorcode = errorcode
        self.errormsg = errormsg
        
    def __str__(self):
        if six.PY2:
            return tobinary('{}:{}'.format(self.errorcode,self.errormsg))
        else:
            return totext('{}:{}'.format(self.errorcode,self.errormsg))

if __name__ == '__main__':
    main()