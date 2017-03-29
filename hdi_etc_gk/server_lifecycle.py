# -*- coding: utf-8 -*-
"""
Created on Wed Mar 29 11:46:03 2017

@author: gkanarek
"""

from __future__ import print_function

def on_server_loaded(server_context):
    print("Server Loaded!")
    print(server_context)
    
def on_server_unloaded(server_context):
    print("Server unloaded!")
    print(server_context)

def on_session_created(server_context):
    print("Session created")
    print(server_context)

def on_session_destroued(server_context):
    print("Session destroyed!")
    print(server_context)