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
        self.nb_created_pages = 0

    def __repr__(self):
        class_name = self.__class__.__name__

        return (
            '<%(class_name)s created_webentities=%(created_webentities)s'
            ' nb_created_pages=%(nb_created_pages)s>'
        ) % {
            'class_name': class_name,
            'created_webentities': self.created_webentities,
            'nb_created_pages': self.nb_created_pages
        }

    def __dict__(self):
        return {
            'created_webentities': self.created_webentities,
            'nb_created_pages': self.nb_created_pages
        }

    def __iadd__(self, other):
        self.created_webentities.update(other.created_webentities)
        self.nb_created_pages += other.nb_created_pages
        return self
