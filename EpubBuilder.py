#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Sat Aug 13 03:10:27 UTC 2011
# Modified :
###

import os
import re

from pikaurdlib.XMLDocument import *
from pikaurdlib import util

class EpubBuilder:
  '''Using text file with some tags like "<img> <chapter>" to build an epub file'''
  __version__ = (0, 0, 0)
  def __init__(self, path='', uuid=1):
    self.path = os.path.join(path, '{v[0]}{v[1]}{v[2]}epubtmp'.format(v=EpubBuilder.__version__))
    self.uuid = uuid

  def createMimetype(self):
    name = 'mimetype'
    content = 'application/epub+zip'
    createFile(name, content, self.path)

  def createContainer(self):
    xml = XMLDocument()
    container = XMLElement('container')
    container.addAttribute('version', '1.0')
    container.addAttribute('xmlns', 'urn:oasis:names:tc:opendocument:xmlns:container')
    rootFiles = XMLElement('rootfiles')
    rootFiles.addElement(XMLElement('rootfile').addAttribute('full-path', 'OEBPS/epb.opf').addAttribute('media-type', 'application/oebps-package+xml'))
    container.addElement(rootFiles)
    xml.addElement(container)
    createFile('container.xml', xml.create(), os.path.join(self.path, 'META-INF'))

  def createFolders(self):
    leaf = ['META-INF', 'OEBPS', 'OEBPS/css', 'OEBPS/images']
    for e in leaf:
      os.makedirs(os.path.join(self.path, e))

class Chapter:
  ''' A epub chapater object '''
  def __init__(self, index, title, content, pretty=False):
    '''
    create a new object
    index for toc. Index of current chapter
    '''
    self.index = index
    self.title = title
    self.content = self.__convertContentToXML(content)
    self.pretty = pretty
    

  def __convertContentToXML(self, content):
    content = util.encodeXML(content)
    content = XMLText(re.sub('\n', '<br/>', content), noEscape=True)
    return content

  def write(self):
    createFile(self.index+'.xhtml', self.__str__(), '')

  def __str__(self):
    xml = XMLDocument('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">')
    html = XMLElement('html')
    html.addAttribute('xml:lang', 'en')
    html.addAttribute('xmlns', 'http://www.w3.org/1999/xhtml')
    head = XMLElement('head')
    title = XMLElement('title')
    title.addElement(XMLText(self.title))
    head.addElement(title)
    html.addElement(head)

    body = XMLElement('body')
    body.addAttribute('style', 'white-space:pre-wrap')
    body.addElement(self.content)
    html.addElement(body)
    xml.addElement(html)
    return xml.create(self.pretty)

def createFile(name, content, path, encoding='utf8'):
  with open(os.path.join(path, name), 'w', encoding=encoding) as f:
    f.write(content)
