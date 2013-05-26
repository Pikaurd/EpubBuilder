#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Sat Aug 13 03:10:27 UTC 2011
# Modified :
###

import os
import re
import shutil
import tempfile
import zipfile

from pikaurdlib.xmldocument import *
from pikaurdlib import util

class EpubBuilder:
  '''Using text file with some tags like "<img> <chapter>" to build an epub file'''
  __version__ = (0, 1, 3)
  def __init__(self, path='', uuid=1):
    self.txtPath = path
    self.path = os.path.join(tempfile.mkdtemp(), '{v[0]}{v[1]}{v[2]}epubtmp'.format(v=EpubBuilder.__version__))
    self.uuid = uuid
    self.metaInfo = readMetaInfo(path)
    self.oebpsPath = os.path.join(self.path, 'OEBPS')

  def createFolders(self):
    leaf = ['META-INF', 'OEBPS', 'OEBPS/css', 'OEBPS/images']
    for e in leaf:
      os.makedirs(os.path.join(self.path, e))
    if self.metaInfo.get('imgDir') != None:
      imgDirPath = os.path.join(os.path.dirname(self.txtPath), self.metaInfo.get('imgDir'))
      for img in [e for e in os.listdir(imgDirPath) if not e.startswith('.')]:
        shutil.copy2(imgDirPath+os.sep+img, os.path.join(self.path,'OEBPS/images'))

  def createMimetype(self):
    name = 'mimetype'
    content = 'application/epub+zip'
    createFile(name, content, self.path)

  def createCSSFile(self):
    path = os.path.join(self.path, 'OEBPS/css/main.css')
    with open(path, 'w') as f:
      f.write('body { white-space: pre-wrap; }\n')
      f.write('h2 { text-align: center; }\n')

  def createContainer(self):
    xml = XMLDocument()
    container = XMLElement('container')
    container.addAttribute('version', '1.0')
    container.addAttribute('xmlns', 'urn:oasis:names:tc:opendocument:xmlns:container')
    rootFiles = XMLElement('rootfiles')
    rootFiles.addElement(XMLElement('rootfile').addAttribute('full-path', 'OEBPS/content.opf').addAttribute('media-type', 'application/oebps-package+xml'))
    container.addElement(rootFiles)
    xml.addElement(container)
    createFile('container.xml', xml.create(), os.path.join(self.path, 'META-INF'))

  def createChapters(self):
    self.titles = txtParseAndCreateChapter(self.txtPath, path=self.oebpsPath)

  def createTOCncx(self):
    title = self.metaInfo.get('title')
    author = self.metaInfo.get('author')
    toc = TOCncx(title, author, self.titles, self.uuid)
    toc.writeTo(self.oebpsPath)

  def createContentOPF(self):
    title = self.metaInfo.get('title')
    author = self.metaInfo.get('author')
    coverImagePath = self.metaInfo.get('coverImage')
    contentOPF = ContentOpf(title, self.uuid, author, 'zh-CN', self.oebpsPath, coverImagePath)
    contentOPF.writeTo()

  def clear(self):
    ''' Delete tmp files'''
    print('Deleting ' + self.path)
    #os.remove(self.path)
    
  @staticmethod
  def nameVersion():
    return 'EpubBuilder at {}'.format(EpubBuilder.__version__)

class Chapter:
  ''' A epub chapater object '''
  def __init__(self, index, title, content, path=''):
    '''
    create a new object
    index for toc. Index of current chapter
    '''
    self.index = index
    self.title = title
    self.content = self.__convertContentToXML(content)
    self.path = path
    

  def __convertContentToXML(self, content):
    content = '<h2>' + self.title + '</h2>' + content # Title
    return XMLText(re.sub('\n', '<br/>', content), noEscape=True)

  def write(self, pretty=False):
    createFile(self.index+'.xhtml', self.create(pretty), self.path) 

  def __str__(self):
    return self.create(self, False)

  def create(self, pretty):
    xml = XMLDocument('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">')
    html = XMLElement('html')
    html.addAttribute('xml:lang', 'en')
    html.addAttribute('xmlns', 'http://www.w3.org/1999/xhtml')
    head = XMLElement('head')
    cssLink = XMLElement('link')
    cssLink.addAttribute('rel', 'stylesheet')
    cssLink.addAttribute('type', 'text/css')
    cssLink.addAttribute('href', 'css/main.css')
    head.addElement(cssLink)
    title = XMLElement('title')
    title.addElement(XMLText(self.title))
    head.addElement(title)
    html.addElement(head)

    #TODO add external module to config format
    body = XMLElement('body')
    div = XMLElement('div')
    div.addElement(self.content)
    body.addElement(div)
    html.addElement(body)
    xml.addElement(html)
    return xml.create(pretty)
    
class TOCncx:
  '''toc.ncx entity'''
  def __init__(self, title, author, chapterTitles, uid):
    self.title = title
    self.author = author
    self.chapterTitles = chapterTitles
    self.uid = uid

  def writeTo(self, path):
    #createFile(name, content, path, encoding)
    createFile('toc.ncx', self.create(), path)

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
    # docAuthor
    docTitle = XMLElement('docAuthor')
    docTitle.addElement(XMLElement('text').addElement(XMLText(self.author)))
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
  def __init__(self, title, uid, creator='EpubBuilder', language='en-US', baseDir='', coverImg=''):
    #TODO add cover to epub
    self.title = title
    self.isbn = str(uid)
    self.creator = creator
    self.lang = language
    self.baseDir = baseDir
    self.coverImage= coverImg

  def writeTo(self):
    createFile('content.opf', self.create(), self.baseDir)

  def addCoverToManifest(self, manifest):
    if self.coverImage == '' or self.coverImage == None: return

    mani_cover = self.__createItem('cover', 'chapter-1.xhtml')
    mani_coverImg = self.__createItem('cover-image', os.path.join('images', self.coverImage), 'image/jpeg')
    manifest.addElement(mani_cover)
    manifest.addElement(mani_coverImg)
    
  def create(self):
    self.getChapters()
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
    identifier = XMLElement('dc:identifier').addAttribute('id', 'ISBN').addElement(XMLText(self.isbn))
    metadata.addElement(identifier)
    lang = XMLElement('dc:language').addElement(XMLText(self.lang))
    metadata.addElement(lang)
    meta_cover = XMLElement('meta')
    meta_cover.addAttribute('name', 'cover')
    meta_cover.addAttribute('content', 'cover-image')
    metadata.addElement(meta_cover)
    package.addElement(metadata)

    # manifest
    manifest = XMLElement('manifest')
    manifest.addElement(self.__createItem('ncx', 'toc.ncx', 'application/x-dtbncx+xml'))
    self.__addItems(manifest)
    self.addCoverToManifest(manifest)
    package.addElement(manifest)

    # spine
    package.addElement(self.__createSpine())

    # guide 
    guide = XMLElement('guide')
    ref = XMLElement('reference')
    ref.addAttribute('type', 'cover')
    ref.addAttribute('title', 'Cover Image')
    ref.addAttribute('href', 'chapter-1.html')
    guide.addElement(ref)
    package.addElement(guide)
    return xml.create(pretty=True)

  def __addItems(self, manifest):
    dirPath = self.baseDir + os.sep
    for e in self.chapters:
      # e[:-6] is strip file extensition '.xhmlt'
      manifest.addElement(self.__createItem(e[:-6], e, 'application/xhtml+xml'))
    for e in [i for i in os.listdir(self.baseDir+os.sep+'images') if not i.startswith('.')]:
      name = os.path.splitext(e)[0]
      manifest.addElement(self.__createItem(name, os.path.join('images', e), 'image/jpeg'))


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
    # add cover
    cover = XMLElement('itemref')
    cover.addAttribute('idref', 'cover')
    spine.addElement(cover)
    # /add cover
    for ch in self.chapters:
      if ch == 'chapter-1.xhtml':  # skip chapter-1 
        continue                   # 'cause it using cover
      spine.addElement(self.__createItemRef(ch[:-6]))
    return spine

  def __createItemRef(self, idRef, linear=None):
    ''' Return a itemref element for tag spine'''
    itemref = XMLElement('itemref')
    itemref.addAttribute('idref', idRef)
    if linear != None:
      itemref.addAttribute('linear', linear)
    return itemref

  def getChapters(self):
    self.chapters = [e for e in os.listdir(self.baseDir) if e.startswith('chapter-') and e.endswith('xhtml')]
    self.chapters.sort(key=lambda x:int(x[8:-6]))

#for unit test
  def createItem(self, rid, href, mediaType):
    return self.__createItem(rid, href, mediaType)

def createFile(name, content, path, encoding='utf8'):
  with open(os.path.join(path, name), 'w', encoding=encoding) as f:
    f.write(content)

###########################################################################
def removeImgTag(x):
  ''' Remove #[img:xxx]# tag, replace with html image tag '''
  xs = x.split('\n')
  result = []
  for s in xs:
    if s.startswith('#[') and not s.startswith('#[img'): continue
    if s.startswith('#[imgDir'): continue
    if s.startswith('#[img'):
      result.append(addImageIfNeed(s))
      continue
    result.append(s)
  return '\n'.join(result)

###########################################################################

def txtParseAndCreateChapter(filePath, encoding='utf8', imgBaseDir='', path=''):
  titles = []
  titlePattern = '(?<=#\[chapter:)[^\]]*(?=\]#)'
  with open(filePath, encoding=encoding) as f:
    c = f.read()
    titles = re.findall(titlePattern, c)
    titles.insert(0, 'Cover')
    cs = re.split('#\[chapter:[^\]]*\]#', c)

    assert(len(titles) == len(cs))

    for i in range(len(cs)):
      fileName = 'chapter-{}'.format(i + 1)
      #content = titles[i] + '\n' + removeImgTag(cs[i])
      content = removeImgTag(cs[i])
      createChapter(fileName, titles[i], content, path)

  return titles     

def createChapter(fileName, title, content, path):
  ch = Chapter(fileName, title, content, path)
  ch.write()
  
def getChapter(x):
  pattern = '(?<=#\[chapter:)[^\]]*(?=\])'
  try:
    result = re.search(pattern, x).group()
  except:
    result = ''
  return result
#  if len(result) != 1:
#    return ''
#  return result[0][10:-2]  #drop prefix and suffix

def isBlank(x, allowWhiteSpace=False):
  if allowWhiteSpace:
    return len(x) == 0
  return len(x.strip()) == 0

def addImageIfNeed(x, path=''):
  pattern = '(?<=#\[img:)[^#]*(?=\]#)'
  search_result = re.search(pattern, x)
  if not search_result:
    return x
  imageName = os.path.basename(search_result.group())
  imgPath = os.path.join('images', path , imageName)
  imgObj = XMLElement('img')
  imgObj.addAttribute('src', imgPath)
  imgObj.addAttribute('alt', imageName)
  return imgObj.create()

def readMetaInfo(filePath, encoding='utf8'):
  metaSearch = re.compile(r'#\[(\w+):([^]].*)\]#')
  metaInfo = {}
  with open(filePath, encoding=encoding) as f:
    tmp = f.readline()
    while '#[headend]#' not in tmp:
      if tmp.strip() == '':
        continue
      k, v = metaSearch.search(tmp).groups()
      metaInfo[k] = v
      tmp = f.readline()
  return metaInfo
    
def create_archive(name, path):
  '''Create the ZIP archive.  The mimetype must be the first file in the archive 
  and it must not be compressed.'''

  epub_name = '{}.epub'.format(name)

  # The EPUB must contain the META-INF and mimetype files at the root, so  
  # we'll create the archive in the working directory first and move it later
  os.chdir(path)    

  # Open a new zipfile for writing
  epub = zipfile.ZipFile(epub_name, 'w')

  # Add the mimetype file first and set it to be uncompressed
  epub.write('mimetype', compress_type=zipfile.ZIP_STORED)
  
  # For the remaining paths in the EPUB, add all of their files
  # using normal ZIP compression
  for p in [e for e in os.listdir('.') if os.path.isdir(e)]:
    for f in os.listdir(p):
      if os.path.isdir(os.path.join(p,f)):
        for t in os.listdir(os.path.join(p,f)):
          epub.write(os.path.join(p, f, t), compress_type=zipfile.ZIP_DEFLATED)
      epub.write(os.path.join(p, f), compress_type=zipfile.ZIP_DEFLATED)
  epub.close()

  # move file to desktop
  os.system('mv "{}" ~/Desktop/'.format(epub_name))

if __name__ == '__main__':
  import sys
  print(txtParseAndCreateChapter(sys.argv[1]))
