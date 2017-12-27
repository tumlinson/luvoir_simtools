import os
from astropy.table import Table, vstack 
import numpy as np 

def convert_to_catalog(table, initial_mass): # takes in astropy table containing the CMD 
    
    number_of_stars = 10000  
    out_table = Table([[0], [0], [0.], [0.], [0.], [0.], [0.], [0.]], 
                          names=('ageindex', 'metalindex', 'logage', 'logz', 'Mass','gmag','rmag', 'grcolor')) 

    metallicities = np.unique(table['LOGZ'])  
    print("unique metallicities: ", metallicities) 

    for metal_index, metallicity in zip([0,1,2,3,4], metallicities): 

        #select out the rows with this metallicity and do the following on them only: 
        ztable = table[table['LOGZ'] == metallicity] 

        ages = np.unique(ztable['LOGAGE'])  
        print("unique ages: ", ages) 

        age_indices = np.arange(np.size(ages), dtype=int) 
        for unique_age, age_index in zip(ages, age_indices): 

            print("computing a catalog for age = ", age_index, unique_age) 
    
            iage = [(ztable['LOGAGE'] > unique_age-0.01) & (ztable['LOGAGE'] < unique_age+0.01)] 
    
            cumimf = np.cumsum(ztable['LOGIMFWEIGHT'][iage])
            cumimf = cumimf / np.max(cumimf) 
     
            # still need to work out normalization for number of stars given input mass 
        
            random_variates = np.random.random(number_of_stars) 
            random_masses = np.interp(random_variates, cumimf, ztable['MASS'][iage]) 
        
            interpolated_rmag = np.interp(random_masses, ztable['MASS'][iage], ztable['UVIS_F814W'][iage]) 
            r_noise = np.random.normal(0.0, 0.01, np.size(random_masses)) * interpolated_rmag # TOTALLY MADE UP NOISE DO NOT RELY ON THIS 
            interpolated_rmag = interpolated_rmag + r_noise 
            interpolated_gmag = np.interp(random_masses, ztable['MASS'][iage], ztable['UVIS_F606W'][iage]) 
            g_noise = np.random.normal(0.0, 0.01, np.size(random_masses)) * interpolated_gmag # TOTALLY MADE UP NOISE DO NOT RELY ON THIS 
            interpolated_gmag = interpolated_gmag + g_noise 
        
            index = np.full(np.size(random_masses), age_index, dtype=int)
            ages_for_table = random_masses * 0.0 + unique_age 
            metallicities_for_table = ages_for_table * 0.0 + metallicity 
            metal_indices_for_table = index * 0 + metal_index 
            print('index',np.size(index))
            print('ages',np.size(ages_for_table))
            print('metal',np.size(metallicities_for_table)) 
            print('random',np.size(random_masses)) 
            print('interpg',np.size(interpolated_gmag))
            print('interpr',np.size(interpolated_rmag))
            age_table = Table([index, metal_indices_for_table, ages_for_table, metallicities_for_table, random_masses,  
                                interpolated_gmag, interpolated_rmag, interpolated_gmag-interpolated_rmag], 
                                names=('ageindex', 'metalindex', 'logage', 'logz', 'Mass','gmag','rmag', 'grcolor')) 
       
            out_table = vstack([out_table, age_table]) 

    return out_table
   

def load_datasets(): #load in the basic CMD / FSPS dataset 

    cwd = os.getenv('LUVOIR_SIMTOOLS_DIR')
    #data_path = cwd+'/data/basic_ssp.fits'
    data_path = cwd+'/data/cmd_grid.fits'

    print('Loading Data from {} ! '.format(data_path))
    if not os.path.isabs(data_path):
        config_dir = os.path.split(self.config_path)[0]
        data_path = os.path.join(config_dir, data_path)

    if not os.path.exists(data_path):
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

