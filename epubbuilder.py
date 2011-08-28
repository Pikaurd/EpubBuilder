#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Sat Aug 13 03:10:27 UTC 2011
# Modified :
###

import os
import re

from pikaurdlib.xmldocument import *
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

  @staticmethod
  def nameVersion():
    return 'EpubBuilder at {}'.format(EpubBuilder.__version__)

class Chapter:
  ''' A epub chapater object '''
  def __init__(self, index, title, content):
    '''
    create a new object
    index for toc. Index of current chapter
    '''
    self.index = index
    self.title = title
    self.content = self.__convertContentToXML(content)
    

  def __convertContentToXML(self, content):
#    content = util.encodeXML(content)
    content = XMLText(re.sub('\n', '<br/>', content), noEscape=True)
    return content

  def write(self, pretty=False):
    createFile(self.index+'.xhtml', self.create(pretty), '')

  def __str__(self):
    return self.create(self, False)

  def create(self, pretty):
    xml = XMLDocument('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">')
    html = XMLElement('html')
    html.addAttribute('xml:lang', 'en')
    html.addAttribute('xmlns', 'http://www.w3.org/1999/xhtml')
    head = XMLElement('head')
    title = XMLElement('title')
    title.addElement(XMLText(self.title))
    head.addElement(title)
    html.addElement(head)

    #TODO add external module to config format
    body = XMLElement('body')
    body.addAttribute('style', 'white-space:pre-wrap')
    body.addElement(self.content)
    html.addElement(body)
    xml.addElement(html)
    return xml.create(pretty)
    
class TOCncx:
  '''toc.ncx entity'''
  def __init__(self, title, chapterTitles, uid):
    self.title = title
    self.chapterTitles = chapterTitles
    self.uid = uid

  def create(self):
    xml = XMLDocument('<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">')
    # root element ncx
    ncx = XMLElement('ncx')
    ncx.addAttribute('xmlns', 'http://www.daisy.org/z3986/2005/ncx/')
    ncx.addAttribute('version', '2005-1')
    # head
    head = XMLElement('head')
    head.addElement(self.__addMeta('uid', self.uid))
    head.addElement(self.__addMeta('depth', 1))
    head.addElement(self.__addMeta('generator', EpubBuilder.nameVersion()))
    head.addElement(self.__addMeta('totalPageCount', 0))
    head.addElement(self.__addMeta('maxPageNumber', 0))
    ncx.addElement(head)
    # docTitle
    docTitle = XMLElement('docTitle')
    docTitle.addElement(XMLElement('text').addElement(XMLText(self.title)))
    ncx.addElement(docTitle)
    # navMap
    navMap = XMLElement('navMap')
#    navMap = self.__addNavPoints(navMap)
    self.__addNavPoints(navMap)
    ncx.addElement(navMap)
    xml.addElement(ncx)
    return xml.create(pretty = True)
    
  def __addMeta(self, name, content):
    meta = XMLElement('meta')
    meta.addAttribute('name', 'dtb:'+name)
    meta.addAttribute('content', content)
    return meta

  def __addNavPoints(self, navMap):
    index = 1
    for chapterTitle in self.chapterTitles:
      navMap.addElement(self.__addNavPoint(index, chapterTitle))
      index += 1
    return navMap
    
  def __addNavPoint(self, playOrder, title):
    chapter = 'chapter-{}.xhtml'.format(playOrder)
    navPoint = XMLElement('navPoint')
    navPoint.addAttribute('id', chapter)
    navPoint.addAttribute('playOrder', playOrder)
    # navLabel
    navLabel = XMLElement('navLabel')
    navLabel.addElement(XMLElement('text').addElement(XMLText(title)))
    navPoint.addElement(navLabel)
    # content
    content = XMLElement('content')
    content.addAttribute('src', chapter)
    navPoint.addElement(content)
    return navPoint

class ContentOpf:
  ''' Entity of content.opf'''
  def __init__(self, title, uid, creator='EpubBuilder', language='en-US', baseDir=''):
    #TODO add cover to epub
    self.title = title
    self.isbn = uid
    self.creator = creator
    self.lang = language
    self.baseDir = os.path.join(baseDir, 'OEBPS')

  def create(self):
    self.getChapters(self.baseDir)
    xml = XMLDocument()
    # root tag -> package
    package = XMLElement('package')
    package.addAttribute('xmlns', 'http://www.idpf.org/2007/opf')
    package.addAttribute('xmlns:dc', 'http://purl.org/dc/elements/1.1/')
    package.addAttribute('unique-identifier', 'ISBN')
    package.addAttribute('version', '2.0')
    xml.addElement(package)
    # meta data
    metadata = XMLElement('metadata')
    title = XMLElement('dc:title').addElement(XMLText(self.title))
    metadata.addElement(title)
    creator = XMLElement('dc:creator').addElement(XMLText(self.creator))
    metadata.addElement(creator)
    identifier = XMLElement('dc:idntifier').addAttribute('id', 'isbn').addElement(XMLText(self.title))
    metadata.addElement(identifier)
    lang = XMLElement('dc:language').addElement(XMLText(self.lang))
    metadata.addElement(lang)
    package.addElement(metadata)
    # mainfest
    mainfest = XMLElement('mainfest')
    mainfest.addElement(self.__createItem('ncx', 'toc.ncx', 'application/x-dtbncx+xml'))
    self.__addItems(mainfest)
    package.addElement(mainfest)
#    mainfest.addElement(self.__addItem())
    # spine
    package.addElement(self.__createSpine())
    # guide 
    guide = XMLElement('guide')
    ##TODO GUIDE for cover and toc
    return xml.create(pretty=True)

  def __addItems(self, mainfest):
    dirPath = self.baseDir + os.sep
    for e in self.chapters:
      # e[:-6] is strip file extensition '.xhmlt'
      mainfest.addElement(self.__createItem(e[:-6], e, 'application/xhtml+xml'))

  def __createItem(self, rid, href, mediaType='application/xhtml+xml'):
    item = XMLElement('item')
    item.addAttribute('id', rid)
    item.addAttribute('href', href)
    item.addAttribute('media-type', mediaType)
    return item

  def __createSpine(self):
    ''' Create a element spine for metadata'''
    spine = XMLElement('spine')
    spine.addAttribute('toc', 'ncx')
    for ch in self.chapters:
      spine.addElement(self.__createItemRef(ch[:-6]))
    return spine

  def __createItemRef(self, idRef, linear=None):
    ''' Return a itemref element for tag spine'''
    itemref = XMLElement('itemref')
    itemref.addAttribute('idref', idRef)
    if linear != None:
      itemref.addAttribute('linear', linear)
    return itemref

  def getChapters(self, path):
    self.chapters = [e for e in os.listdir() if e.startswith('chapter-') and e.endswith('xhtml')]

#for unit test
  def createItem(self, rid, href, mediaType):
    return self.__createItem(rid, href, mediaType)

def createFile(name, content, path, encoding='utf8'):
  with open(os.path.join(path, name), 'w', encoding=encoding) as f:
    f.write(content)

class TextSplitter:
  '''Split source file'''
  def getHead(self, fileHandle):
    '''get meta info (head) from handle'''
    x = fileHandle.readline()
    head = []
    while not self.__headEnd(x):
      if x.lstrip().startswith('#'):
        head.append(x)
      x = fileHandle.readline()
    return head

  def __headEnd(self, x):
    return '#[headend]#' in x

def txtParseAndCreateChapter(filePath, encoding='utf8', imgBaseDir=''):
  buffer = ''
  index = 0
  title = 'info'
  titles = []
  with open(filePath, encoding=encoding) as f:
    tmp = util.encodeXML(f.readline())
    while not isBlank(tmp):
      while isBlank(getChapter(tmp)) and not isBlank(tmp, True):
        buffer += addImageIfNeed(tmp, imgBaseDir)
        tmp = util.encodeXML(f.readline())

      buffer = buffer.strip()
      fileName = 'chapter-{}'.format(index)
      if len(buffer) > 0:
        titles.append(title)
        ch = Chapter(fileName, title, buffer)
        ch.write()
        buffer = ''
        index += 1
        title = getChapter(tmp)
        tmp = util.encodeXML(f.readline())
  return titles

def getChapter(x):
  pattern = '''\#\[chapter:    # head
        [
          \u0021-\u007e       #ascii symbols
          \u3041-\u30ff       #hiragana & katakana
          \u4e00-\u9fc4       #CJK common characters
        ]+
        \]\#
  '''
  result = re.findall(pattern, x, re.VERBOSE)
  if len(result) != 1:
    return ''
  return result[0][10:-2]  #drop prefix and suffix

def isBlank(x, allowWhiteSpace=False):
  if allowWhiteSpace:
    return len(x) == 0
  return len(x.strip()) == 0

def addImageIfNeed(x, path=''):
  pattern = r'(?<=#\[img:)[\w\d/\.]+]#'
  matched = re.findall(pattern, x)
  if len(matched) != 1:
    return x
  imgPath = os.path.join(path , matched[0][:-2])
  return XMLElement('img').addAttribute('src', imgPath).create()




