# =============================================================================
# Walk History
# =============================================================================
#
# Class representing a walk history in the Traph.
#


class WalkHistory(object):

    def __init__(self):

        # Properties
        self.last_webentity_id = None
        self.last_webentity_id_position = -1
        self.last_webentity_creationrule_id = None
        self.last_webentity_creationrule_id_position = -1
        self.last_webentity_prefix = ''
        self.node_id = -1
        self.success = False
