######################################################################
#                              METADATA                              #
######################################################################


class Metadata:
    def __init__(self, no_progress, no_color, yes, silent, verbose, debug, logfile, virus_check, reduce_package, rate_limit):
        self.no_progress = no_progress
        self.no_color = no_color
        self.yes = yes
        self.silent = silent
        self.verbose = verbose
        self.debug = debug
        self.logfile = logfile
        self.virus_check = virus_check
        self.reduce_package = reduce_package
        self.rate_limit = rate_limit
