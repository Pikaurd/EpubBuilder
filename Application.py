#!/usr/bin/python3
import sys
import argparse

from os.path import basename

from epubbuilder import *

def createEpub(src, fname):
# builder = EpubBuilder('epubDir/md.txt')
  builder = EpubBuilder(src)
  builder.createFolders()
  builder.createMimetype()
  builder.createCSSFile()
  builder.createContainer()
  builder.createChapters()
  builder.createTOCncx()
  builder.createContentOPF()
  create_archive(fname, builder.path)
  builder.clear()

if __name__ == "__main__":
  desc = 'EpubBuilder: A tool convert formatted text to epub'
  parser = argparse.ArgumentParser(description=desc)
  parser.add_argument('src', help='Source text file')
  parser.add_argument('-f'
                     , '--filename'
                     , type=str
                     , help='Target file name')
  args = parser.parse_args()

  src = args.src
  filename = basename(src)
  if args.filename:
    filename = args.filename

  print('Convert {} -> {}'.format(src, filename))
  createEpub(src, filename)
  sys.exit(0)
