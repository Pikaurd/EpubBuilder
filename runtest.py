#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Sat Aug 13 02:28:07 UTC 2011
# Modified :
###

import os
import re
import unittest

from epubbuilder import *

from pikaurdlib.xmldocument import XMLElement
from pikaurdlib.util import encodeXML


class TestBuildEpub(unittest.TestCase):
  def setUp(self):
    self.path = os.getcwd() + os.path.sep + 'epubDir/'
    self.epubBuilder = EpubBuilder(self.path)

  @unittest.skip("run once enough")
  def test_createFile(self):
    fileName = 'mimetype'
    fileContent = 'application/epub+zip'
    self.epubBuilder.createMimetype()
    with open(self.path+fileName) as realFile:
      self.assertEqual(fileContent, realFile.read())

  @unittest.skip("run once enough")
  def test_createFolders(self):
    self.epubBuilder.createFolders()
    self.epubBuilder.createMimetype()
    self.epubBuilder.createContainer()
    #FIXME 

class TestChapter(unittest.TestCase):
  @unittest.skip('skip')
  def test___str__(self):
    c = Chapter(1, 'chapter1')
    print(c)
    
  def test_convertContentToXML(self):
    content = '''Hello epub python world!
This is my first generated chapter'''
    c = Chapter(1, 'chapter1', content)
    expect = 'Hello epub python world!<br/>This is my first generated chapter'
    self.assertEqual(expect, c.content.create())

  @unittest.skip("run once enough")
  def test_write(self):
    self.maxDiff = 6000
    with open('devlog.txt') as f:
      content = f.read()
    ch = Chapter('2', 'dev log', content)
    with open('1.xhtml') as f:
      expect = f.read()
    self.assertEqual(expect, ch.__str__())

@unittest.skip('skip')
class TestTextSplitter(unittest.TestCase):
  def test_getHead(self):
    splitter = TextSplitter()
    with open('epubDir/head.txt') as f:
      head = splitter.getHead(f)
    print(head)


#@unittest.skip('skip')
class TestTempSplitAndCreateFile(unittest.TestCase):
  def test_hasChapter(self):
    self.assertEqual('chapter', getChapter('fdajklfsdj#[chapter:chapter]#'))

  def test_addImageIfNeed(self):
    self.assertEqual('<img src="images/img.jpg" alt="img.jpg"/>', addImageIfNeed('ax#[img:md/img.jpg]#suffix', ''))
    self.assertEqual('def test_split(self):', addImageIfNeed('def test_split(self):', 'path'))

  def test_isBlank(self):
    self.assertTrue(isBlank(''))
    self.assertTrue(isBlank('   '))
    self.assertFalse(isBlank('1'))
    self.assertFalse(isBlank(' ', True))

  @unittest.skip('tmp')
  def test_txtParseAndCreateChapter(self):
    txtParseAndCreateChapter('epubDir/head.txt', imgBaseDir='epubDir')

  @unittest.skip('tmp')
  def test_split(self):
    buffer = ''
    index = 0
    title = 'info'
    with open('epubDir/head.txt') as f:
      tmp = encodeXML(f.readline())
      while not isBlank(tmp):
        while isBlank(getChapter(tmp)) and not isBlank(tmp, True):
          buffer += addImageIfNeed(tmp, 'epubDir')
          tmp = f.readline()

        print('chapter change:\t'+title)
        buffer = buffer.strip()
        fileName = 'chapter-{}'.format(index)
        if len(buffer) > 0:
          ch = Chapter(fileName, title, buffer)
          ch.write()
          buffer = ''
          index += 1
          title = getChapter(tmp)
          tmp = f.readline()
  
  @unittest.skip('tmp')
  def test_readMetaInfo(self):
    print('MetaInfo:')
    print(readMetaInfo('epubDir/head.txt'))

@unittest.skip('tmp')
class TestTocncx(unittest.TestCase):
  @unittest.skip('succ')
  def test_create(self):    
    toc = TOCncx('title', ['ch1', 'ch2', 'ch3'], 'thisiduid')
    print(toc.create())
    
class TestContentOpf(unittest.TestCase):
  @unittest.skip(1)
  def test_create(self):
    opf = ContentOpf('title', 'uid', 'creator', language='zh-CN')
    print(opf.create())

  @unittest.skip(1)
  def test_createItem(self):
    opf = ContentOpf('title', 'uid', 'creator', language='zh-CN')
    ncx = opf.createItem('ncx', 'toc.ncx', 'application/x-dtbncx+xml').create()
    self.assertEqual('<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>', ncx)
    
#@unittest.skip('tmp')
class TestApplication(unittest.TestCase):
  def test_create(self):
    builder = EpubBuilder('epubDir/md.txt')
    builder.createFolders()
    builder.createMimetype()
    builder.createContainer()
    builder.createChapters()
    builder.createTOCncx()
    builder.createContentOPF()
    create_archive('md', 'epubDir/003epubtmp/')

if __name__ == "__main__":
  unittest.main()

