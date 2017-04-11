#!/usr/bin/env python
"""
Created on Sat Oct 15 10:59:16 2016

@author: gkanarek
"""

from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

from syotools.persistence import JSON


class PersistentModel(object):
    """
    A base framework for creating persistent model profiles.
    
    Protocols:
        Currently, the only implemented persistence protocol is JSON. I chose
        JSON for several reasons:
            - It's human readable
            - It handles dictionaries natively, making for easy defaulting
            - It's easily sent & received via HTTP
            - It's very well supported & editable in many languages
        However, JSON is not particularly sophisticated, so new protocols may
        be implemented in the future.
    
    Attributes:
        _default_model      - The defaults dictionary for the model. This should 
                              be set by subclasses.
        _protocol_registry  - A registry of persistence protocols which are
                              currently implemented.
        _tracked_attributes - A list of attributes which should be stored on
                              save.
        _current_protocol   - The current persistence protocol name.
    """
    
    _default_model = {}
    _protocol_registry = {}
    _tracked_attributes = []
    _current_protocol = ''
    
    def __init__(self, **kw):
        """
        This is quite generic; all model-specific customization should be
        handled in the specific model subclass.
        """
        
        #First, load defaults, overwriting with anything specifically set in
        #the instantiation call.
        for attr, val in self._default_model.items():
            self._tracked_attributes.append(attr)
            setattr(self, attr, kw.pop(attr, val))
        
        #Now, set any new attributes not in the defaults
        for attr, val in kw:
            self._tracked_attributes.append(attr)
            setattr(self, attr, val)
        
        json_protocol = JSON(self._default_model)
        self.register_protocol(json_protocol)
        self.set_current_protocol('json', verbose=False)
            
    def register_protocol(self, protocol):
        """
        Add a new (already prepped) protocol to the registry.
        """
        self._protocol_registry[protocol.name] = protocol

    def set_current_protocol(self, new_protocol, verbose=True):
        """
        Choose which protocol to use for model persistence.
        """
        if new_protocol in self._protocol_registry:
            self._current_protocol = new_protocol
            if verbose:
                print("Persistence protocol changed to {}".format(new_protocol))
            
            proto = self._protocol_registry[self._current_protocol]
            self.load_profile = proto.load
            self.save_profile = proto.save
            
        else:
            print("Persistence protocol not recognized; remaining with {}".format(self._current_protocol.name()))
            
    def save(self, jsonfile):
        """
        Use the current persistence protocol to save the model profile.
        """
        persistence = self._protocol_registry[self._current_protocol]
        persistence.save(self, jsonfile)
    
    def load(self, jsonfile):
        """
        Use the current persistence protocol to load parameters from a model
        profile.
        """
        persistence = self._protocol_registry[self._current_protocol]
        new_model = persistence.load(self.__cls__, jsonfile)
        new_model._protocol_registry = self._protocol_registry
        new_model._current_protocol = self._current_protocol
        self = new_model