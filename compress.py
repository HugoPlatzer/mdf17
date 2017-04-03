import os, sys, uuid, argparse

def encodeGM(inFile, outFile, quality):
  os.system("gm convert {} -quality {} {}".format(inFile, quality, outFile))

def decodeGM(inFile, outFile):
  os.system("gm convert {} {}".format(inFile, outFile))

def encodeJxrLib(inFile, outFile, quality):
  os.system("JxrEncApp -i {} -o {} -q {}".format(inFile, outFile, quality))
  
def decodeJxrLib(inFile, outFile):
  os.system("JxrDecApp -i {} -o {}".format(inFile, outFile))

def preprocessImage(fileName):
  originalUncompressed = str(uuid.uuid4()) + ".bmp"
  decodeGM(fileName, originalUncompressed)
  return originalUncompressed

def compressWithEncoder(encoder, inFile, filePrefix, fileEnding, quality):
  outFile = "{}_{}{}".format(filePrefix, str(quality), fileEnding)
  encoder(inFile, outFile, quality)
  outFileSize = os.path.getsize(outFile)
  return (outFile, outFileSize)

def compressToSize(encoder, inFile, fileEnding, qualityRange, targetSize):
  compressionAttempts = []
  filePrefix = str(uuid.uuid4())
  lowerIdx, currentIdx, upperIdx = 0, 0, len(qualityRange) - 1
  while lowerIdx <= upperIdx:
    currentIdx = (lowerIdx + upperIdx) / 2
    currentQuality = qualityRange[currentIdx]
    #print((lowerIdx, currentIdx, upperIdx, currentQuality))
    outFile, outFileSize = compressWithEncoder(encoder, inFile, filePrefix, fileEnding, currentQuality)
    os.remove(outFile)
    #print(outFileSize)
    if outFileSize <= targetSize:
      lowerIdx = currentIdx + 1
    else:
      upperIdx = currentIdx - 1
    
  outFile, outFileSize = compressWithEncoder(encoder, inFile, filePrefix, fileEnding, qualityRange[currentIdx])
  if outFileSize <= targetSize:
    return outFile
  os.remove(outFile)
  outFile, outFileSize = compressWithEncoder(encoder, inFile, filePrefix, fileEnding, qualityRange[currentIdx - 1])
  return outFile

def switchExtension(fileName, newExtension):
  baseName, extension = os.path.splitext(fileName)
  return baseName + newExtension

def convertImagesInDirectory(inDir, outDir, compressor):
  dirList = os.listdir(inDir)
  for i in range(len(dirList)):
    originalFile = os.path.join(inDir, dirList[i])
    uncompressedOriginal = str(uuid.uuid4()) + ".bmp"
    decodeGM(originalFile, uncompressedOriginal)
    compressedFile = compressor.compress(uncompressedOriginal)
    compressedFileName = switchExtension(os.path.split(originalFile)[1], compressor.extension)
    os.rename(compressedFile, os.path.join(outDir, compressedFileName))
    os.remove(uncompressedOriginal)
    print("{}/{}".format(i + 1, len(dirList)))

class JPGFormat:
  def __init__(self, targetSize):
    self.targetSize = targetSize
    self.qualityRange = range(10, 90)
    self.extension = ".jpg"

  def compress(self, inFileName):
    return compressToSize(encodeGM, inFileName, self.extension, self.qualityRange, self.targetSize)
  
  def uncompress(self, fileName):
    jpgUncompressed = str(uuid.uuid4()) + ".bmp"
    decodeGM(fileName, jpgUncompressed)
    return jpgUncompressed

class JP2Format:
  def __init__(self, targetSize):
    self.targetSize = targetSize
    self.qualityRange = range(10, 90)
    self.extension = ".jp2"

  def compress(self, inFileName):
    return compressToSize(encodeGM, inFileName, self.extension, self.qualityRange, self.targetSize)
  
  def uncompress(self, fileName):
    jp2Uncompressed = str(uuid.uuid4()) + ".bmp"
    decodeGM(fileName, jp2Uncompressed)
    return jp2Uncompressed

class JXRFormat:
  def __init__(self, targetSize):
    self.targetSize = targetSize
    self.qualityRange = range(150, 20, -1)
    self.extension = ".jxr"

  def compress(self, inFileName):
    return compressToSize(encodeJxrLib, inFileName, self.extension, self.qualityRange, self.targetSize)
  
  def uncompress(self, fileName):
    jxrUncompressed = str(uuid.uuid4()) + ".bmp"
    decodeJxrLib(fileName, jxrUncompressed)
    return jxrUncompressed

formatChoices = {"jpg" : JPGFormat, "jp2" : JP2Format, "jxr" : JXRFormat}

parser = argparse.ArgumentParser()
parser.add_argument("inDirectory")
parser.add_argument("outDirectory")
parser.add_argument("fileFormat", choices = formatChoices.keys())
parser.add_argument("targetSize", type = int)
args = parser.parse_args()

compressor = formatChoices[args.fileFormat](args.targetSize)
convertImagesInDirectory(args.inDirectory, args.outDirectory, compressor)
