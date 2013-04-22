#!/usr/bin/python3
import sys

from epubbuilder import *

def createEpub(src, fname):
# builder = EpubBuilder('epubDir/md.txt')
  builder = EpubBuilder(src)
  builder.createFolders()
  builder.createMimetype()
  builder.createContainer()
  builder.createChapters()
  builder.createTOCncx()
  builder.createContentOPF()
  create_archive(fname, builder.path)

if __name__ == "__main__":
  if len(sys.argv) <= 1:
    print("Usage: {} src filename".format(sys.argv[0]))
    sys.exit(1)
  src = sys.argv[1]
  fname = sys.argv[2]
  print("src: {}\nfile name: {}".format(src, fname))
  createEpub(src, fname)
  print("finished")
  sys.exit(0)
