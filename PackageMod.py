# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 10:56:25 2023

@author: STiFU
"""

from zipfile import ZipFile
import os
from datetime import datetime
from glob import glob

def PackageMod(srcPath: str, dstPath: str, lstIgnoredFilePatterns: list = None):
    
    print(f'\nPackaging: {srcPath}')
    
    srcPath = srcPath.strip('\"')
    basePath,modName = os.path.split(srcPath)
    
    if not modName.lower().startswith('mod'):
        raise ValueError('Mod folder does not start with "mod"')
    
    dstPath = dstPath.strip('\"')
    dstPath = os.path.expandvars(dstPath)
    os.makedirs(dstPath, exist_ok = True)
    
    now = datetime.now().strftime("_%Y-%m-%d_%H%M%S")
    zipPath = os.path.join(dstPath, modName+now+'.zip')
    
    print(f'Destination: {zipPath}')   
    
    
    allIgnoredElements = []
    for ignoredPattern in lstIgnoredFilePatterns:
        ignored = glob(os.path.join(srcPath, ignoredPattern), recursive=True)
        allIgnoredElements += [os.path.relpath(abspath, basePath) for abspath in ignored]
    print('\nIgnoring the following files/folders:\n\t'+ '\n\t'.join(allIgnoredElements))        
    
    
    def getRelPath(absPath: str):
        return os.path.relpath(absPath, basePath)
    def getAbsPath(root,leaf):
        return os.path.join(root, leaf)

    
    with ZipFile(zipPath, 'w') as myzip:
        for root,dirs,files in os.walk(srcPath):
            
            # skip ignored dirs
            dirs[:] = [directory for directory in dirs if getRelPath(getAbsPath(root,directory)) not in allIgnoredElements]
            
            for file in files:
                absPath = getAbsPath(root,file)
                relPath = getRelPath(absPath)
                if relPath in allIgnoredElements:
                    continue
                
                myzip.write(absPath, arcname=relPath)
        print(f'\nMod successfully packaged to:\n\t{zipPath}\n')

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Witcher 3 Mod packaging helper', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    
    parser.add_argument('PATH_SRC', help='The mod-path to package.')
    
    parser.add_argument('--IgnoredFilePatterns', nargs='*', metavar='Pattern', default=['.git*', '*.bat'],
                        help='Files/folders matching this pattern will be excluded from packaging.')
    
    parser.add_argument('--DestPath', default='%USERPROFILE%/downloads',
                        help='The path to store the zipped mod to.')
    
    parser.print_help()
    
    args = parser.parse_args()
    
    
    try:
        PackageMod(args.PATH_SRC, args.DestPath, args.IgnoredFilePatterns)
    except Exception as e:
        print(e)
    
    input('Press Enter to exit...')