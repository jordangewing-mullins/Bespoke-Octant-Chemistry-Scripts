"""
This script converts a substance list generated by chemhub into a substance list that searches for other relevant byproducts of Suzuki coupling, Buchwald amination, and amide coupling.
At a more general level, this script allows for well-level specification of leaving groups and can readily be adapted for other chemistries.
"""
import pandas, re
substance_list_infile_name = input('What is the name of your current substance list? (then press Enter) \n')
if not substance_list_infile_name.endswith('.csv'):
    substance_list_infile_name += '.csv' # add file extension if the user didn't

df = pandas.read_csv(substance_list_file_name)
# print(df.head())

coupling_chemistry = input('What coupling chemistry are you doing? Type A for amide coupling, B for Buchwal amination,\n R for reductive amination or S for Suzuki coupling (then press Enter)\n')

def set_coupling_chemistry(coupling_chemistry):
    global suzuki, buchwald, amide_coupling
    if 's' in coupling_chemistry.lower():
        suzuki = True
    elif 'b' in coupling_chemistry.lower():
        buchwald = True
    elif 'a' in coupling_chemistry.lower():
        amide_coupling = True
    elif 'r' in coupling_chemistry.lower():
        reductive_amination = True
    # add some logic about the type of core and fragment (i.e. carboxylic acid, amine, aryl halide)

# dictionary where every key is a unique molecular formula of a fragment and the value is its cognate leaving group molecular formula
# Note: this is experiment specific
fragment_leaving_groups = {'OCNT-0380949':'B1O2C6H12','OCNT-0380946':'B1O2H2','OCNT-0380945':'B1O2C6H12','OCNT-0380943':'B1O2H2','OCNT-0380942':'B1O2C6H12','OCNT-0380941':'B1O2H2','OCNT-0380939':'B1O2C6H12','OCNT-0380932':'B1O2H2','OCNT-0380931':'B1O2C6H12','OCNT-0380918':'B1O2H2', 'OCNT-0380948':'B1F3','OCNT-0380947':'B1F3','OCNT-0380944':'B1F3', 'OCNT-0380940':'B1F3' }

def tokenize_molecule(molecule):
    """ this function takes a molecular formula in the form of a string and converts it to a dictionary where each key is an element and its cognate value is the number of times that element is present in the compound
    This function returns that dictionary."""
    tokenized_mol_form = re.findall('[A-Z][a-z]?|\d+|.', molecule)
    for i in range (len(tokenized_mol_form)):
        if tokenized_mol_form[i][0] in '0123456789': # check to see if the string actually represents a number
            tokenized_mol_form[i] = int(tokenized_mol_form[i]) # then change the type of the data to an integer
    mol_form_dict={}
    for i in range(len(tokenized_mol_form)-1):
        if isinstance(tokenized_mol_form[i], str) and isinstance(tokenized_mol_form[i+1], int):
            mol_form_dict.update({tokenized_mol_form[i]:tokenized_mol_form[i+1]})
        elif isinstance(tokenized_mol_form[i], str) and isinstance(tokenized_mol_form[i+1], str): # if there are two back to back elements not separated by a number, then explicitly say we have one of the first element
            mol_form_dict.update({tokenized_mol_form[i]:1})
    if isinstance(tokenized_mol_form[-1], str): # if the molecule ends with a string (i.e. C6H6BrNO) we have to add the last key:value pair to mol_form_dict
        mol_form_dict.update({tokenized_mol_form[-1]:1})
    return mol_form_dict

def subtract_LG_from_mol_form(LG_dictionary, OG_mol_form_dictionary):
    """This function takes two dictionaries: one for the leaving group and one for the original molecular formula from which you want the leaving group to leave.
    Each is a dictionary where every key is a unique molecular formula of a fragment and the value is its cognate leaving group molecular formula
    """
    product_dictionary = OG_mol_form_dictionary # initialize dictionary for the OG molecular formula - the leaving group
    for key in list(LG_dictionary.keys()):
        product_dictionary.update({key: OG_mol_form_dictionary[key]-LG_dictionary[key]}) # remove LG from mol form
    return product_dictionary

def add_two_molecules(added_molecule_dictionary, OG_mol_form_dictionary):
    """This function takes two dictionaries: one for the leaving group and one for the original molecular formula from which you want the leaving group to leave.
    Each is a dictionary where every key is a unique molecular formula of a fragment and the value is its cognate leaving group molecular formula
    """
    product_dictionary = OG_mol_form_dictionary # initialize dictionary for the OG molecular formula - the leaving group
    for key in list(added_molecule_dictionary.keys()):
        product_dictionary.update({key: OG_mol_form_dictionary[key]+added_molecule_dictionary[key]}) # remove LG from mol form
    return product_dictionary

def remove_zeros(molecule_dictionary):
    """remove elements that have a zero after them in the final molecular formula after the leaving group has been removed.
    For example it converts the molecular formula C6H6Br0N2O2 into C6H6N2O2"""
    for x in list(molecule_dictionary.keys()):
        if molecule_dictionary[x] == 0:
            del molecule_dictionary[x]
    return molecule_dictionary


def homocoupling(molecule, leaving_group):
    """this function takes two inputs, the molecule refers to a string that represents a molecular formula. The leaving_group input is a string that represents the one (or two) character long leaving group that would
    leave EACH molecule if a homocoupling event occurred."""
    molecule_dict = tokenize_molecule(molecule)
    doubled_molecule_dict = dict({k: 2*v for k,v in molecule_dict.items()})

    leaving_group_dict = tokenize_molecule(leaving_group)
    doubled_leaving_group_dict = dict({k: 2*v for k,v in leaving_group_dict.items()})

    product_dictionary = remove_zeros(subtract_LG_from_mol_form(doubled_leaving_group_dict, doubled_molecule_dict))

    final_homocoupling_product_string = ''.join("{!s}{!r}".format(k,v) for (k,v) in product_dictionary.items())
    # print(final_homocoupling_product_string)
    return final_homocoupling_product_string

def amide_coupling_homocoupling(molecule):
    # you should probably combine this with the function above. this function is largely redundant with it.
    molecule_dict = tokenize_molecule(molecule)
    doubled_molecule_dict = dict({k: 2*v for k,v in molecule_dict.items()})
    leaving_group_dict = tokenize_molecule('H2O')
    product_dictionary = remove_zeros(subtract_LG_from_mol_form(doubled_leaving_group_dict, doubled_molecule_dict))
    final_homocoupling_product_string = ''.join("{!s}{!r}".format(k,v) for (k,v) in product_dictionary.items())
    return final_homocoupling_product_string


def protodeboronation(molecule, leaving_group):
    molecule_dict = tokenize_molecule(molecule)
    leaving_group_dict = tokenize_molecule(leaving_group)

    # add one Hydrogen to the fragment, which replaces the boron species that leaves
    molecule_dict['H'] += 1

    # subtract the leaving group from the molecular formula
    product_dictionary = remove_zeros(subtract_LG_from_mol_form(leaving_group_dict, molecule_dict))
    final_protodeboronation_product_string = ''.join("{!s}{!r}".format(k,v) for (k,v) in product_dictionary.items())
    return final_protodeboronation_product_string

def oxazalone(molecule):
    molecule_dict = tokenize_molecule(molecule)
    leaving_group_dict = tokenize_molecule('H2O')  # this is a dehydration reeaction
    # subtract the leaving group from the molecular formula
    product_dictionary = remove_zeros(subtract_LG_from_mol_form(leaving_group_dict, molecule_dict))
    final_oxazalone_product_string = ''.join("{!s}{!r}".format(k,v) for (k,v) in product_dictionary.items())
    return final_oxazalone_product_string

def carbamide(molecule, leaving_group):
    # double check that i didn't make up this byproduct. not sure if it is core-specific or if this is a common byproduct. hunch is that it's core-specific
    molecule_dict = tokenize_molecule(molecule)
    if 'O' not in list(molecule_dict.keys()):
        molecule_dict.update({'O':1}) # add a double bonded oxygen 
    else:
        molecule_dict['O'] +=1
    molecule_dict['H'] += 1  # add a hydrogen
    leaving_group_dict = tokenize_molecule(leaving_group)
    product_dictionary = remove_zeros(subtract_LG_from_mol_form(leaving_group_dict, molecule_dict))
    final_carbamide_product_string = ''.join("{!s}{!r}".format(k,v) for (k,v) in product_dictionary.items())
    return final_carbamide_product_string

def activated_ester(molecule, activator):
    molecule_dict = tokenize_molecule(molecule)

    if activator == 'DMTMM':
        activator_added_mol_form = 'C5H7N3O2' # this is the molecular formula of the part that gets added to the carboxylic acid, not the full molecular formula of the activator
    elif activator == 'HATU':
        activator_added_mol_form = 'C5H3N4'
    elif activator == 'HBTU':
        activator_added_mol_form = 'C6H4N4'

    product_dictionary = add_two_molecules(tokenize(activator_added_mol_form), molecule_dict)
    final_product_string = ''.join("{!s}{!r}".format(k,v) for (k,v) in product_dictionary.items())
    return final_product_string

# create substance lists based on the coupling chemistry specified by the user # 
if suzuki:
    # find byproducts
    df['protodeboronation_product'] = [protodeboronation(y,fragment_leaving_groups[x]) for x,y in zip(df['frags'],df['frag_form']) ]
    df['homocoupling_product'] = [homocoupling(y,fragment_leaving_groups[x]) for x,y in zip(df['frags'],df['frag_form']) ]

    # replace existing columns to accomodate new compounds we will be looking at
    df['SubstanceAdduct']=['[M+H]_[M+H]_[M+H]_[M+H]_[M+H]' for x in df['source_well']]
    df['SubstanceName']=['Desired_Core_Fragment_Protodeboronation_homocoupling' for x in df['source_well']]
    df['SubstanceType'] = ['Product_StartingMaterial_StartingMaterial_Product_Product' for x in df['source_well']]
    df['SubstanceColor'] = ['Green_Red_Blue_Black_Yellow' for x in df['source_well']]
    df['IdentitySignal'] = ['<COMPOSITE>_<COMPOSITE>_<COMPOSITE>_<COMPOSITE>_<COMPOSITE>' for x in df['source_well']]
    df['SubstanceConfirmationMode'] = ['MSOnly_MSOnly_MSOnly_MSOnly_MSOnly' for x in df['source_well']]
    df['SignalAssignmentMode'] = ['MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther' for x in df['source_well']]
    df['Formula'] = df['Formula'] + '_'+df['protodeboronation_product']+'_'+df['homocoupling_product']
    df.drop(['protodeboronation_product', 'homocoupling_product'], axis=1)

elif buchwald:
    df['carbamide'] = [carbamide(x, 'Br') for x in df['core_form'] ] # idk if this is acutally a comon byproduct or if it just was for the core I was looking ar
    
    # might be cool to be able to see if theere are any reactions where the Cl was accidentally the leaving group (on a core with both a Br and a Cl)
    
    # replace existing columns to accomodate new compounds we will be looking at
    df['SubstanceAdduct']=['[M+H]_[M+H]_[M+H]_[M+H]' for x in df['source_well']]
    df['SubstanceName']=['Desired_Core_Fragment_Carbamide' for x in df['source_well']]
    df['SubstanceType'] = ['Product_StartingMaterial_StartingMaterial_Product' for x in df['source_well']]
    df['SubstanceColor'] = ['Green_Red_Blue_Black' for x in df['source_well']]
    df['IdentitySignal'] = ['<COMPOSITE>_<COMPOSITE>_<COMPOSITE>_<COMPOSITE>' for x in df['source_well']]
    df['SubstanceConfirmationMode'] = ['MSOnly_MSOnly_MSOnly_MSOnly' for x in df['source_well']]
    df['SignalAssignmentMode'] = ['MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther' for x in df['source_well']]
    df['Formula'] = df['Formula'] + '_'+df['carbamide']
    del df['carbamide']  

elif amide_coupling:
    df['oxazalone'] = [oxazalone(x.split('_')[0]) for x in df['Formula'] ]
    # add homocoupling here with some kind of logic defined above that will 
    if core_type == 'Ca':
       df['homocoupling'] = [amide_coupling_homocoupling(x) for x in df['core_form']]
       df['activated_ester'] = [activated_ester(x, activator_mol_form) for x in df['core_form']]
    else:
       df['homocoupling'] = [amide_coupling_homocoupling(x) for x in df['frag_form']] 
       df['activated_ester'] = [activated_ester(x, activator_mol_form) for x in df['frag_form'] ]

    # replace existing columns to accomodate new compounds we will be looking at
    df['SubstanceAdduct']=['[M+H]_[M+H]_[M+H]_[M+H]_[M+H]' for x in df['source_well']]
    df['SubstanceName']=['Desired_Core_Fragment_Oxazalone_homocoupling' for x in df['source_well']]
    df['SubstanceType'] = ['Product_StartingMaterial_StartingMaterial_Product_Product' for x in df['source_well']]
    df['SubstanceColor'] = ['Green_Red_Blue_Black_Yellow' for x in df['source_well']]
    df['IdentitySignal'] = ['<COMPOSITE>_<COMPOSITE>_<COMPOSITE>_<COMPOSITE>_<COMPOSITE>' for x in df['source_well']]
    df['SubstanceConfirmationMode'] = ['MSOnly_MSOnly_MSOnly_MSOnly_MSOnly'' for x in df['source_well']]
    df['SignalAssignmentMode'] = ['MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther_MSOnlyAndOther' for x in df['source_well']]
    df['Formula'] = df['Formula'] + '_'+df['oxazalone'] + '_' + df['homocoupling']
    df.drop(['oxazalone', 'homocoupling'], axis=1)

# save the new substance list with a modified name
substance_list_outfile_name = substance_list_infile_name.split('.')[0]+'_NEW.csv'
df.to_csv(substance_list_outfile_name,index=False)
