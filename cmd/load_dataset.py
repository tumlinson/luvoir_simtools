from os import path
from astropy.table import Table, vstack 
import numpy as np 

def convert_to_catalog(table, initial_mass): 

    # takes in astropy table containing the CMD 
    number_of_stars = 100000. 
    
    out_table = Table([[0], [0.], [0.], [0.], [0.], [0.]], 
                          names=('ageindex', 'logage', 'Mass','gmag','rmag', 'grcolor')) 

    ages = np.unique(table['LOGAGE'])  
    print("unique values: ", ages) 
    age_indices = np.arange(np.size(ages), dtype=int) 
    for unique_age, age_index in zip(ages, age_indices): 

        print("computing a catalog for age = ", age_index, unique_age) 

        iage = [(table['LOGAGE'] > unique_age-0.01) & (table['LOGAGE'] < unique_age+0.01)] 

        cumimf = np.cumsum(table['LOGIMFWEIGHT'][iage])
        cumimf = cumimf / np.max(cumimf) 
 
        # still need to work out normalization for number of stars given input mass 
    
        random_variates = np.random.random(number_of_stars) 
        random_masses = np.interp(random_variates, cumimf, table['MASS'][iage]) 
    
        interpolated_rmag = np.interp(random_masses, table['MASS'][iage], table['UVIS_F814W'][iage]) + np.random.normal(0.0, 0.05, np.size(random_masses)) 
        interpolated_gmag = np.interp(random_masses, table['MASS'][iage], table['UVIS_F606W'][iage]) + np.random.normal(0.0, 0.05, np.size(random_masses)) 
    
        ages = random_masses * 0.0 + unique_age 
        index = np.full(np.size(random_masses), age_index, dtype=int)
        print(index) 
        age_table = Table([index, ages, random_masses, interpolated_gmag, interpolated_rmag, interpolated_gmag-interpolated_rmag], 
                              names=('ageindex', 'logage', 'Mass','gmag','rmag', 'grcolor')) 
       
        out_table = vstack([out_table, age_table]) 

    return out_table
   

def load_datasets(): #load in the basic CMD / FSPS dataset 

    data_path = '/Users/tumlinson/Dropbox/LUVOIR/SYOTools/luvoir_simtools/data/basic_ssp.fits'

    print('Loading Data from {} ! '.format(data_path))
    if not path.isabs(data_path):
        config_dir = path.split(self.config_path)[0]
        data_path = path.join(config_dir, data_path)

    if not path.exists(data_path):
        raise IOError('Unable to find input dataset: "{}"'.format(data_path))

    if data_path.endswith(".fits"):
        data_table = Table.read(data_path)
        if ('LOGIMFWEIGHT' in data_table.keys()): data_table['LOGIMFWEIGHT'] = 10.**data_table['LOGIMFWEIGHT']

        initial_mass = 1000. 						# just for testing purposes 
        catalog = convert_to_catalog(data_table, initial_mass) 

        data_table['grcolor'] = data_table['UVIS_F606W'] - data_table['UVIS_F814W']
        data_table['rmag'] = -1. * data_table['UVIS_F814W']
        data_table['logage'] = data_table['LOGAGE']
        data_table['phase'] = data_table['PHASE']
        data_table['UVIS_F814W'] *= -1.
        data_table['UVIS_F606W'] *= -1.
        dataframe = data_table.to_pandas()
        catalog['rmag'] *= -1. 
        catalog['gmag'] *= -1. 
        dataframe = catalog.to_pandas() 
    else:
        raise IOError("Unknown data file type; only .fits currently supported")

    return dataframe

