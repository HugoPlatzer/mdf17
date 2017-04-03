import os, sys, uuid, argparse

def encodeGM(inFile, outFile, quality):
  os.system("gm convert {} -quality {} {}".format(inFile, quality, outFile))

def decodeGM(inFile, outFile):
  os.system("gm convert {} {}".format(inFile, outFile))

def encodeJxrLib(inFile, outFile, quality):
  os.system("JxrEncApp -i {} -o {} -q {}".format(inFile, outFile, quality))

def preprocessImage(fileName):
  originalUncompressed = str(uuid.uuid4()) + ".bmp"
  decodeGM(fileName, originalUncompressed)
  return originalUncompressed

def compressorFunction(encoder, inFile, filePrefix, fileEnding, qualityRange):
  def compress(encoder, inFile, filePrefix, fileEnding, qualityRange, qualityIdx):
    quality = qualityRange[qualityIdx]
    outFile = "{}_{}{}".format(filePrefix, str(quality), fileEnding)
    encoder(inFile, outFile, quality)
    outFileSize = os.path.getsize(outFile)
    return (outFile, outFileSize)
  
  return lambda qualityIdx : compress(encoder, inFile, filePrefix, fileEnding, qualityRange, qualityIdx)

def compressToSize(encoder, inFile, fileEnding, qualityRange, targetSize):
  filePrefix = str(uuid.uuid4())
  lowerIdx, currentIdx, upperIdx = 0, 0, len(qualityRange) - 1
  compressAtQuality = compressorFunction(encoder, inFile, filePrefix, fileEnding, qualityRange)
  
  while lowerIdx <= upperIdx:
    currentIdx = (lowerIdx + upperIdx) / 2
    outFile, outFileSize = compressAtQuality(currentIdx)
    os.remove(outFile)
    if outFileSize <= targetSize:
      lowerIdx = currentIdx + 1
    else:
      upperIdx = currentIdx - 1
    
  outFile, outFileSize = compressAtQuality(currentIdx)
  if outFileSize <= targetSize:
    return (outFile, qualityRange[currentIdx], outFileSize)
  elif currentIdx > 0:
    currentIdx -= 1
  else:
    currentIdx = 0
    
  os.remove(outFile)
  outFile, outFileSize = compressAtQuality(currentIdx)
  return (outFile, qualityRange[currentIdx], outFileSize)

def switchExtension(fileName, newExtension):
  baseName, extension = os.path.splitext(fileName)
  return baseName + newExtension

def convertImagesInDirectory(inDir, outDir, compressor):
  dirList = os.listdir(inDir)
  for i in range(len(dirList)):
    originalFile = os.path.join(inDir, dirList[i])
    uncompressedOriginal = str(uuid.uuid4()) + ".bmp"
    decodeGM(originalFile, uncompressedOriginal)
    compressedFile, quality, fileSize = compressor.compress(uncompressedOriginal)
    compressedFileName = switchExtension(os.path.split(originalFile)[1], compressor.extension)
    os.rename(compressedFile, os.path.join(outDir, compressedFileName))
    os.remove(uncompressedOriginal)
    print("{}/{} {} q = {} size = {}".format(i + 1, len(dirList), dirList[i], quality, fileSize))
    if fileSize > compressor.targetSize:
      print("could not meet target size!")
      sys.exit(1)

class JPGFormat:
  def __init__(self, targetSize):
    self.targetSize = targetSize
    self.qualityRange = range(10, 90)
    self.extension = ".jpg"

  def compress(self, inFileName):
    return compressToSize(encodeGM, inFileName, self.extension, self.qualityRange, self.targetSize)

class JP2Format:
  def __init__(self, targetSize):
    self.targetSize = targetSize
    self.qualityRange = range(10, 90)
    self.extension = ".jp2"

  def compress(self, inFileName):
    return compressToSize(encodeGM, inFileName, self.extension, self.qualityRange, self.targetSize)

class JXRFormat:
  def __init__(self, targetSize):
    self.targetSize = targetSize
    self.qualityRange = range(150, 20, -1)
    self.extension = ".jxr"

  def compress(self, inFileName):
    return compressToSize(encodeJxrLib, inFileName, self.extension, self.qualityRange, self.targetSize)

formatChoices = {"jpg" : JPGFormat, "jp2" : JP2Format, "jxr" : JXRFormat}

parser = argparse.ArgumentParser()
parser.add_argument("inDirectory")
parser.add_argument("outDirectory")
parser.add_argument("fileFormat", choices = formatChoices.keys())
parser.add_argument("targetSize", type = int)
args = parser.parse_args()

compressor = formatChoices[args.fileFormat](args.targetSize)
convertImagesInDirectory(args.inDirectory, args.outDirectory, compressor)
