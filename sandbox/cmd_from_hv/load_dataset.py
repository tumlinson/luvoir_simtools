from os import path
from astropy.table import Table

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
        data_table['g-r'] = data_table['UVIS_F606W'] - data_table['UVIS_F814W']
        data_table['grcolor'] = data_table['UVIS_F606W'] - data_table['UVIS_F814W']
        data_table['dropoff_x'] = data_table['g-r']
        data_table['dropoff_y'] = -1 * data_table['UVIS_F814W']
        data_table['dropoff_age'] = data_table['LOGAGE']
        data_table['UVIS_F814W'] *= -1.
        data_table['UVIS_F606W'] *= -1.
        dataframe = data_table.to_pandas()
    else:
        raise IOError("Unknown data file type; only .fits currently supported")

    return dataframe

