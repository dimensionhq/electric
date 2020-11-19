######################################################################
#                          REGISTRY SNAPSHOT                         #
######################################################################


class RegSnapshot:
    def __init__(self, sys_value, sys_length, env_value, env_length):
        self.sys_value = sys_value
        self.sys_length = sys_length
        self.env_value = env_value
        self.env_length = env_length