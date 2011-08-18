#!/usr/bin/python3
# -*- coding: UTF-8 -*-

###
# Created  :Sat Aug 13 02:28:07 UTC 2011
# Modified :
###

import os
import unittest

from EpubBuilder import EpubBuilder
from EpubBuilder import Chapter


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
    
  @unittest.skip('skip')
  def test_convertContentToXML(self):
    content = '''Hello epub & python world!
This is my first generated chapter'''
    c = Chapter(1, 'chapter1', content)
    expect = 'Hello epub &amp; python world!<br/>This is my first generated chapter'
    self.assertEqual(expect, c.content.create())

  @unittest.skip('skip')
  def test_write(self):
    self.maxDiff = 6000
    with open('devlog.txt') as f:
      content = f.read()
    ch = Chapter('2', 'dev log', content)
    with open('1.xhtml') as f:
      expect = f.read()
    self.assertEqual(expect, ch.__str__())

class TestParseTxt(unittest.TestCase):
  def test_parse(self):
    parseTxt = ParseTxt()
    with open('epubDir/md.txt') as f:
      txt = f.read()
    charpters = parseTxt.parse(txt)






if __name__ == "__main__":
  unittest.main()

