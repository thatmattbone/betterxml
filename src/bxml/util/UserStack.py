
"""
 Simple Stack class for Python
"""

from UserList import UserList

class UserStack(UserList):
    def __init__(self, initStack=None):
        if initStack:
            if isinstance(initStack, UserList):
                UserList.__init__(self, initStack.data)
            elif type(initStack) == type([]):
                UserList.__init__(self, initStack)
            else:
                raise "[] or UserList Required"
        else:
            UserList.__init__(self)
   
    def push(self, obj):
        UserList.append(self, obj)

    def pop(self):
        if len(self) > 0:
            return UserList.pop(self)
        else:
            raise "UserStack Underflow"

    def top(self):
        if len(self) > 0:
            return self[-1]
        else:
            raise "UserStack Overflow"
     
    def empty(self):
        return len(self) == 0

    def notEmpty(self):
        return not empty(self)

