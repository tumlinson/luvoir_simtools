# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 13:37:35 2017

@author: gkanarek

A file input widget, adapted from here: http://stackoverflow.com/a/42613897/3225754
"""

from bokeh.core.properties import String
from bokeh.models import LayoutDOM

IMPL = """
import * as p from "core/properties"
import {LayoutDOM, LayoutDOMView} from "models/layouts/layout_dom"

export class FileInputView extends LayoutDOMView
  initialize: (options) ->
    super(options)
    input = document.createElement("input")
    input.type = "file"
    input.onchange = () =>
      @model.value = input.value
    @el.appendChild(input)

export class FileInput extends LayoutDOM
  default_view: FileInputView
  type: "FileInput"
  @define {
    value: [ p.String ]
  }
"""

class FileInput(LayoutDOM):
    """
    A rough FileInput widget for Bokeh.
    """
    __implementation__ = IMPL
    value = String()