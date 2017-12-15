#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 18 08:43:23 2016

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

#Protocols:
import json

#Utilities:
import astropy.units as u
import numpy as np

#### Base Protocol class

class Protocol(object):
    """
    A class for defining new persistence protocols; the only one currently
    implemented is JSON.
    
    Each protocol needs to include four functions:
        1. An encode function
        2. A decode function
        3. A save function
        4. A load function
    
    Each protocol also needs to store units along with values in some way,
    and must at least handle attributes which are arrays or dicts.
    """
    
    def save(self, *args, **kwargs):
        raise NotImplementedError("This protocol is incomplete!")
    def load(self, *args, **kwargs):
        raise NotImplementedError("This protocol is incomplete!")
    def encode(self, *args, **kwargs):
        raise NotImplementedError("This protocol is incomplete!")
    def decode(self, *args, **kwargs):
        raise NotImplementedError("This protocol is incomplete!")

    
    def __init__(self, defaults_dict):
        self._defaults = defaults_dict


####JSON protocol implementation

class JSON(Protocol):
    
    name = 'json'
    
    def encode(self, entry):
        """
        Encode a single model attribute as a tuple or dict, for JSON storage.
        
        We need to handle units, so we'll be storing values as tuples of (value,
        unit). We'll use FITS-standard unit formatting, for easy integration with 
        the astropy.io.fits API. 
        """
        if isinstance(entry, u.Quantity):
            unit = entry.unit.to_string('fits')
            if isinstance(entry.value, np.ndarray):
                return (entry.value.tolist(), unit)
            return (entry.value, unit)
        elif isinstance(entry, dict):
            return {k: self.encode(v) for k,v in entry.items()}
        else:
            return entry
    
    def decode(self, attr, entry):
        """
        Decode an individual entry in a JSON profile into the appropriate 
        Quantity(s). This method uses the 'generic' units formatting, to allow 
        for user-defined profiles that don't use the FITS standard.
        
        Special cases:
          - If the entry is not a dict or a tuple, it is returned without
            modification.
          - If the entry is a dict, recurse on each element.
          - If the entry is a list, convert it to a numpy array.
          - If the units can't be parsed, use the default unit for that
            attribute if one is available, otherwise use 
            astropy.units.UnrecognizedUnit.
        """
        if not isinstance(entry, (dict, tuple)):
            return entry #This doesn't have units.
        if isinstance(entry, dict):
            return {k: self.decode(k, v) for k,v in entry.items()}
        val, units = entry
        try:
            units = u.Unit(units)
        except ValueError:
            msg = "Attribute {} did not have valid units; ".format(attr)
            if attr in self._defaults:
                def_unit = self._defaults[attr]
                msg += "using model's default units of {}".format(def_unit)
                units = u.Unit(def_unit)
            else:
                msg += "using astropy.units.UnrecognizedUnit"
                units = u.UnrecognizedUnit
            print(msg)
        if isinstance(val, (list, tuple)):
            val = np.array(val)
        return val * units
    
    def load(self, model_class, jsonfile):
        """
        Load a model profile from a json file. This is a very basic
        persistence model, which can absolutely be made more sophisticated.
        
        The only difference from standard JSON is that we want to parse each
        attribute through the protocol decoder. 
        """
    
        profile = {}
    
        try:
            with open(jsonfile) as f:
                profile_dict = json.load(f)
            
            #Reconstruct the profile
            for attr, entry in profile_dict.items():
                profile[attr] = self.decode(attr, entry)
            
        except FileNotFoundError:
            print("File {} not found; using default profile.".format(jsonfile))
        except NotImplementedError:
            print("This protocol is not implemented; using default profile.")
            
        return model_class(**profile)

    def save(self, model, jsonfile):
        """
        Store a model profile into a json file. This is a very basic
        persistence model, which can absolutely be made more sophisticated.
        
        To handle units, we'll pass everything through the encoder.
        """
        
        profile = {}
        
        for attr in model._tracked_attributes:
            val = getattr(model, attr)
            profile[attr] = self.encode(val)
        
        with open(jsonfile, 'w') as f:
            json.dump(f, profile, sort_keys=True, indent=4)