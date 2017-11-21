#!/usr/bin/env python
"""
Created on Tue Apr 25 11:44:58 2017

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import astropy.units as u
import numpy as np

u.magnitude_zero_points.enable()

class JsonUnit(object):
    """
    A quick and dirty solution for making units storable via JSON. This is
    used in both the persistence subpackage (when implementing the JSON protocol),
    and in the actual tools, so that we can use astropy units along with
    Bokeh server.
    """
    
    def __init__(self, quant=0, unit=""):
        self._array = False
        if isinstance(quant, u.Quantity):
            if unit:
                quant = quant.to(u.Unit(unit))
            self._value, self._unit = self._grab_from_quantity(quant)
        else:
            self._unit = self._grab_unit(unit)
            self._value = self._grab_value(quant)
    
    def __repr__(self):
        return self.use.__repr__

    def _grab_from_quantity(self, quantity):
        return self._grab_value(quantity.value), self._grab_unit(quantity.unit)
    
    def _grab_value(self, value):
        if isinstance(value, np.ndarray):
            self._array = True
            return value.tolist()
        else:
            self._array = False
            return value
    
    def _grab_unit(self, unit):
        if isinstance(unit, (u.UnitBase, u.FunctionUnitBase)):
            return unit.to_string()
        return unit
    
    @property
    def unit(self):
        return u.Unit(self._unit)
    
    @unit.setter
    def unit(self, new_unit):
        self._unit = self._grab_unit(new_unit)
    
    @property
    def value(self):
        if self._array:
            return np.array(self._value)
        return self._value
    
    @value.setter
    def value(self, new_val):
        self._value = self._grab_value(new_val)    
    
    @property
    def use(self):
        return self.value * self.unit
    
    @use.setter
    def use(self, new_quant):
        if not isinstance(new_quant, u.Quantity):
            raise TypeError("JsonUnit.use expects a Quantity object.")
        self._value, self._unit = self._grab_from_quantity(new_quant)
        
    def convert(self, new_unit):
        """
        Setting instance.unit changes the unit directly, and doesn't alter the
        value(s).
        """
    
        quant = self.use.to(new_unit)
        self._value, self._unit = self._grab_from_quantity(quant)
    
    def encode_json(self):
        return ("JsonUnit", {"unit": self._unit, "value": self._value})
    
    @classmethod
    def decode_json(cls, serialized):
        if isinstance(serialized, np.ndarray) or "JsonUnit" not in serialized:
            raise ValueError("Serialized element is not a JsonUnit")
        junit = cls()
        judict = serialized[1]
        junit._unit = judict["unit"]
        if isinstance(judict["unit"],list):
            junit._array = True
        junit._value = judict["value"]
        return junit

def recover_quantities(*args):
    """
    Utility function to convert a number of JsonUnit instances into their
    Quantity counterparts, so that calculations may be done.
    """
    return [jsu.use for jsu in args]

def pre_encode(quant):
    """
    We only REALLY want to store the JSON serialization, a lot of the time.
    """
    
    if not isinstance(quant, u.Quantity):
        return quant
    
    return JsonUnit(quant).encode_json()

def pre_decode(serialized):
    """
    Often, we don't actually need to store a JsonUnit representation of
    a quantity, we just want the Quantity version.
    """
    
    try:
        quant = JsonUnit.decode_json(serialized)
    except (AttributeError, ValueError, TypeError):
        return serialized #not a JsonUnit serialization
    
    return quant.use
        
        