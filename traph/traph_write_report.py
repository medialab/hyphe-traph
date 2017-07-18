# =============================================================================
# Traph Write Report Class
# =============================================================================
#
# Class representing the report we will emit on write operations to be able
# to return some stats & the created webentities to the user.
#


class TraphWriteReport(object):

    def __init__(self):

        # Properties
        self.created_webentities = {}
