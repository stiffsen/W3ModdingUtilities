# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 08:36:47 2023

@author: STiFU
"""

import os
import shutil


def GenerateDummyTranslations(srcFilepath: str, dstPath = None):
    
    if os.path.splitext(srcFilepath)[-1] == '.csv':
        srcFilepath, baseStrFile = os.path.split(srcFilepath)
    else:
        baseStrFile = ''
        for file in ['en.w3strings.csv', 'en.csv']:
            if os.path.exists(os.path.join(srcFilepath, file)):
                baseStrFile = file
                break
    baseNaming = baseStrFile[baseStrFile.find('.'):]
    
    if dstPath is None:
        dstPath = srcFilepath
    else:
        os.makedirs(dstPath, exist_ok=True)
    
    absBaseFile = os.path.join(srcFilepath, baseStrFile)
    if not os.path.isfile(absBaseFile):
        raise FileNotFoundError(f'{absBaseFile}')
        
    with open(absBaseFile, 'r') as f:
        linesBase = f.readlines()
        
    languages = {'ar':'ar',
                 'br':'br',
                 'cn':'cleartext',
                 'cz':'cz',
                 'de':'de',
                 'en':'en',
                 'es':'es',
                 'esmx':'esmx',
                 'fr':'fr',
                 'hu':'hu',
                 'it':'it',
                 'jp':'jp',
                 'kr':'kr',
                 'pl':'pl',
                 'ru':'ru',
                 'tr':'tr',
                 'zh':'zh'}
    
    for languageKey, languageId in languages.items():
        
        absDstPath = os.path.join(dstPath, f'{languageKey}{baseNaming}')
        if os.path.exists(absDstPath):
            # Already available
            print(f'Skipping: {absDstPath}')
            continue
        
        print(f'Writing: {absDstPath}')
        
        linesDst = list(linesBase)
        linesDst[0] = f';meta[language={languageId}]\n'
        
        with open(absDstPath, 'w') as f:
            f.writelines(linesDst)
   
    
    
def encodeAllCsv(srcPath: str, idspace: int, dstPath: str = None):
    
    if dstPath is None:
        dstPath = os.path.join(srcPath, '..', 'content')
    else:
        os.makedirs(dstPath, exist_ok=True)
        
    csvFiles = [file for file in os.listdir(srcPath) if file.endswith('.csv')]
    for csv in csvFiles:
        abspathSrc = os.path.join(srcPath, csv)
        os.system(f'w3strings.exe --encode "{abspathSrc}" --id-space {idspace}')
        
        dstFile = csv[:csv.find('.')] + '.w3strings'
        shutil.move(abspathSrc+'.w3strings', os.path.join(dstPath, dstFile))
        
        os.remove(abspathSrc + '.w3strings.ws')
    
    
    
def decodeAllW3strings(srcPath: str, dstPath: str = None):
    
    if os.path.splitext(srcPath)[-1] == '.w3strings':
        srcPath, file = os.path.split(srcPath)
        files = [file]
    else:
        files = [file for file in os.listdir(srcPath) if file.endswith('.w3strings')]
        
    if dstPath is None:
        dstPath = os.path.join(srcPath, '..', 'localization')
    os.makedirs(dstPath, exist_ok = True)
            
    for file in files:
        abspathSrc = os.path.join(srcPath, file)
        os.system(f'w3strings.exe --decode "{abspathSrc}"')
        
        if dstPath:
            shutil.move(abspathSrc+'.csv', os.path.join(dstPath, file+'.csv'))



if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='w3strings.exe wrapper') #, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    
    parser.add_argument('--OutputPath', '-o', metavar='PATH',
                       help='The output path where the generated files shall be stored. If none is provided, command specific default paths will be used.')
    
    groupdummy = parser.add_argument_group(description='Generate dummy localization files, so non-provided translations dont show up as empty')
    groupdummy.add_argument('--GenerateDummyLocalizations', '-g', metavar='PATH', 
                        help='Generates dummy localizations based on a given w3string file. If only a basepath is given, i.e., no w3strings file, en.csv or en.w3strings.csv will be used automatically.')
    
    groupEncoding = parser.add_argument_group(description='Encoding w3strings')
    groupEncoding.add_argument('--Encode', '-e', metavar='PATH',
                        help='Encode all the csv files in the passed directory to w3strings.')
    
    groupEncoding.add_argument('--idspace', '-i', metavar='NexusModsId', type=int,
                       help='The id space to use. It is recommended to use the ID of your mod on NexusMods. If not provided in commandline, user will be querried.')
    
    groupDecoding = parser.add_argument_group(description='Decoding w3strings')
    groupDecoding.add_argument('--Decode', '-d', metavar='PATH',
                               help='Decode all w3strings in the given directory.')
    
    parser.print_help()    
    
    
    args = parser.parse_args()
    
    if args.GenerateDummyLocalizations:
        # Testing: --GenerateDummyLocalizations "x:\Games\SteamLibrary\steamapps\common\The Witcher 3\Mods\modBetterMovement\localization" --OutputPath "x:\Games\SteamLibrary\steamapps\common\The Witcher 3\Mods\modBetterMovement\localization\testGen"
        GenerateDummyTranslations(args.GenerateDummyLocalizations, args.OutputPath)
        
    elif args.Encode:
        # Testing: --Encode "x:\Games\SteamLibrary\steamapps\common\The Witcher 3\Mods\modBetterMovement\localization" --idspace 7591 --OutputPath "x:\Games\SteamLibrary\steamapps\common\The Witcher 3\Mods\modBetterMovement\localization\testEnc"
        if not args.idspace:
            args.idspace = int(input('Enter id-space (Mod id on NexusMods): '))
        encodeAllCsv(args.Encode, args.idspace, args.OutputPath)
        
    elif args.Decode:
        # Testing: --Decode "x:\Games\SteamLibrary\steamapps\common\The Witcher 3\Mods\modBetterMovement\content" --OutputPath "x:\Games\SteamLibrary\steamapps\common\The Witcher 3\Mods\modBetterMovement\localization\testDec"
        decodeAllW3strings(args.Decode, args.OutputPath)
        
    else:
        print('No command issued...')