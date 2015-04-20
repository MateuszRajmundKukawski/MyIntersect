import os, re, shutil

def sprzataj():
    filePath = 'd:/tempdata/temp/budynki_update_raw_num.shp'
    old_file =  os.path.basename(filePath)[:-4]
    dirPath = 'd:/tempdata/temp/'



    newName = 'Budynki_wynik.shp'
    print old_file
    os.chdir(dirPath)
    os.chdir('..')
    destDir = os.getcwd()+'/'
    os.chdir(dirPath)
    print destDir
    fileList= os.listdir( os.getcwd())
    copyList = []
    for obj in fileList:
        if re.search(old_file, obj):
            print obj
            ext = obj[-4:]
            print ext
            shutil.copy(obj, destDir+newName+ext)
sprzataj()