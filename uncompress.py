import os, argparse
from collections import defaultdict

def convertGM(inFile, outFile):
  os.system("gm convert {} {}".format(inFile, outFile))

def decodeJxrLib(inFile, outFile):
  os.system("JxrDecApp -i {} -o {}".format(inFile, outFile))

def convertImagesInDirectory(inDir, outDir, compressToPNG, decoders):
  dirList = os.listdir(inDir)
  for i in range(len(dirList)):
    compressedImage = os.path.join(inDir, dirList[i])
    compressedBasename, compressedExtension = os.path.splitext(dirList[i])
    uncompressedImage = compressedBasename + ".bmp"
    decoders[compressedExtension](compressedImage, uncompressedImage)
    if compressToPNG:
      pngImage = compressedBasename + ".png"
      convertGM(uncompressedImage, pngImage)
      os.rename(pngImage, os.path.join(outDir, pngImage))
      os.remove(uncompressedImage)
    else:
      os.rename(uncompressedImage, os.path.join(outDir, uncompressedImage))
    print("{}/{}".format(i + 1, len(dirList)))

decoders = defaultdict(lambda : convertGM)
decoders[".jxr"] = decodeJxrLib

parser = argparse.ArgumentParser()
parser.add_argument('-p', action='store_true')
parser.add_argument("inDirectory")
parser.add_argument("outDirectory")
args = parser.parse_args()
convertImagesInDirectory(args.inDirectory, args.outDirectory, args.p, decoders)
