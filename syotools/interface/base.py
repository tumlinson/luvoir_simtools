#!/usr/bin/env python2
"""
Created on Wed Oct 19 12:43:00 2016

@author: gkanarek, tumlinson
"""
from __future__ import (print_function, division, absolute_import, with_statement,
                        nested_scopes, generators)

import yaml
import os

#Import the constructor function factories
from syotools.interface import factory


class SYOParserError(Exception):
    """
    A custom error for problems with parsing the interface files.
    """


class SYOTool(object):
    """
    This is a framework for quickly generating Bokeh tools for Science Yield
    Optimization. Much of the Bokeh machinery will be kept under the hood in
    this class. To create a new tool, simply subclass SYOTool, set some
    parameters, connect with some astronomical models, and output embeddable 
    HTML.
    
    One major update is to use .yaml files as a templating method (a la the
    kv language in Kivy) to allow for quick and easy human-readable Bokeh
    interface construction.
    """
    
    #Here we assign the constructor methods
    mapping_factory = factory.mapping_factory
    sequence_factory = factory.sequence_factory
    scalar_factory = factory.scalar_factory
    figure_constructor = factory.figure_constructor
    document_constructor = factory.document_constructor
    
    def self_constructor(self, loader, tag_suffix, node):
        """
        A multi_constructor for `!self` tag in the interface file.
        """
        yield eval("self"+tag_suffix, globals(), locals())
        
    def tool_preinit(self):
        """
        This should be implemented by the tool subclass, to do any pre-
        initialization steps that the tool requires.
        
        If this is not required, subclass should set `tool_preinit = None`
        in the class definition.
        """
        
        raise NotImplementedError
    
    def tool_postinit(self):
        """
        This should be implemented by the tool subclass, to do any pre-
        initialization steps that the tool requires.
        
        If this is not required, subclass should set `tool_postinit = None`
        in the class definition.
        """
        
        raise NotImplementedError
    
    def __init__(self):
        """
        We need to initialize two dictionary attributes:
            
            self.formats, to include any formatting keywords which are set 
                in a separate string
                
            self.refs, which contains all the specific Bokeh objects which
                are created by the YAML parser.
        
        Then, we need to register all the constructors that we need.
        """
        
        #Allow for pre-init stuff from the tool subclass.
        if self.tool_preinit is not None:
            self.tool_preinit()
        
        #Handle YAML construction
        self.formats = {}
        self.refs = {}
        
        self.document = None
        
        #Register constructors
        for m in factory.mappings:
            yaml.add_constructor(u"!"+m+":", self.mapping_factory(m))
        for s in factory.sequences:
            yaml.add_constructor(u"!"+s+":", self.sequence_factory(s))
        for s in factory.scalars:
            yaml.add_constructor(u"!"+s+":", self.scalar_factory(s))
        
        yaml.add_constructor(u"!Figure:", self.figure_constructor)
        yaml.add_constructor(u"!Document:", self.document_constructor)
        
        yaml.add_multi_constructor(u"!self", self.self_constructor)
        
        self.include_formatting()
        self.parse_interface()
        
        #Allow for post-init stuff from the tool subclass.
        if self.tool_postinit is not None:
            self.tool_postinit()
    
    def include_formatting(self):
        """
        This should simply be a dictionary of formatting keywords.
        """
        if not self.format_string:
            return
        
        self.formats = yaml.load(self.format_string)
    
    def parse_interface(self):
        """
        This is the workhorse YAML parser, which creates the interface based
        on the layout file.
        
        `interface_file` is the path to the interface .yaml file to be parsed.
        """
        
        if not self.interface_file:
            raise NotImplementedError("Interface file required.")
        
        #Read the interface file into a string
        filepath = os.path.abspath(os.path.expanduser(self.interface_file))
        if not os.path.exists(filepath):
            raise SYOParserError("Interface file path does not exist.")
        with open(filepath) as f:
            interface = f.read()
        
        #First, let's make sure that there's a Document in here
        if '!Document' not in interface:
            raise SYOParserError("Interface file must contain a Document tag")
        
        #Now, since we've registered all the constructors, we can parse the 
        #entire string with yaml. We don't need to assign the result to a
        #variable, since the constructors store everything in self.refs
        #(and self.document, for the document)
        
        self.full_stream = list(yaml.load_all(interface))