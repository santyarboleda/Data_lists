from list_eu.utilities import Utilities as eu_utilities
from list_ssus.utilities import Utilities as ssus_utilities
from list_ofac.utilities import Utilities as ofac_utilities
from list_onu.utilities import Utilities as onu_utilities

# get european union terrorists
utl_eu = eu_utilities()
utl_eu.get_data_eu_list()


# get state secretary u.s. terrorists organizations
utl_ssus = ssus_utilities()
utl_ssus.get_data_ssus_list()

# get ofac-clinton list
utl_ofac = ofac_utilities()
utl_ofac.get_data_ofac_list()

# get onu list
utl_onu = onu_utilities()
utl_onu.get_data_onu_list()