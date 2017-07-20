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

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s created_webentities=%(created_webentities)s>'
        ) % {
            'class_name': class_name,
            'created_webentities': self.created_webentities
        }

    def __dict__(self):
        return {
            'created_webentities': self.created_webentities
        }

    def __iadd__(self, other):
        self.created_webentities.update(other.created_webentities)
        return self
