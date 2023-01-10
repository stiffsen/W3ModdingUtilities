# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 08:36:47 2023

@author: STiFU
"""

import os
import shutil

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


def CreateEmptyCsv(dstPath: str, idspace: int, numberOfRowsToCreate: int = None, languageId: str = None):
    
    os.makedirs(dstPath, exist_ok = True)
    
    if not languageId:
        languageId = 'en'
    
    if not numberOfRowsToCreate:
        numberOfRowsToCreate = 2
    
    with open(os.path.join(dstPath, f'{languageId}.csv'), 'w', encoding='utf-8') as f:
        f.write(f';meta[language={languages[languageId]}]\n')
        f.write('; id      |key(hex)|key(str)| text\n')
        for n in range(numberOfRowsToCreate):
            f.write(f'211{idspace:04d}{n:03d}|        |ExampleStringIdentifier{n}|Example String\n')
            

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
   
    
    
def EncodeAllCsv(srcPath: str, idspace: int, dstPath: str = None):
    
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
    
    
    
def DecodeAllW3strings(srcPath: str, dstPath: str = None):
    
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
    
    #%% CLI
    import argparse
    
    parser = argparse.ArgumentParser(description='w3strings.exe wrapper') #, formatter_class=argparse.ArgumentDefaultsHelpFormatter
    
    parser.add_argument('--OutputPath', '-o', metavar='PATH',
                       help='The output path where the generated files shall be stored. If none is provided, command specific default paths will be used.')
    
    parser.add_argument('--idspace', '-i', metavar='NexusModsId', type=int,
                       help='The id space to use when encoding or creating a new csv. It is recommended to use the ID of your mod on NexusMods. If not provided in commandline, user will be querried.')
    
    groupCreate = parser.add_argument_group(description='Create a new localization template.')
    groupCreate.add_argument('--CreateNew','-c', metavar='PATH',
                             help='Create an empty csv files for localization with some example data.')
    groupCreate.add_argument('--LanguageId', metavar='ID', choices=list(languages.keys()),
                             help='The language id for the csv to create.')
    groupCreate.add_argument('--NumStringRows', metavar='NR', type=int,
                             help='The number of example rows to create in the new csv.')
    
    groupdummy = parser.add_argument_group(description='Generate dummy localization files, so non-provided translations dont show up as empty')
    groupdummy.add_argument('--GenerateDummyLocalizations', '-g', metavar='PATH', 
                        help='Generates dummy localizations based on a given w3string file. If only a basepath is given, i.e., no w3strings file, en.csv or en.w3strings.csv will be used automatically.')
    
    groupEncoding = parser.add_argument_group(description='Encoding w3strings')
    groupEncoding.add_argument('--Encode', '-e', metavar='PATH',
                        help='Encode all the csv files in the passed directory to w3strings.')
    
    groupDecoding = parser.add_argument_group(description='Decoding w3strings')
    groupDecoding.add_argument('--Decode', '-d', metavar='PATH',
                               help='Decode all w3strings in the given directory.')
    
    parser.print_help()    
    args = parser.parse_args()
    
    #%% Execute
    
    def GetIdSpace() -> int:
        return args.idspace if args.idspace else int(input('Enter id-space (Mod id on NexusMods): '))
    
    if args.GenerateDummyLocalizations:
        GenerateDummyTranslations(args.GenerateDummyLocalizations, args.OutputPath)
        
    elif args.Encode:
        EncodeAllCsv(args.Encode, GetIdSpace(), args.OutputPath)
        
    elif args.Decode:
        DecodeAllW3strings(args.Decode, args.OutputPath)
        
    elif args.CreateNew:
        CreateEmptyCsv(args.CreateNew, GetIdSpace(), args.NumStringRows, args.LanguageId)
        
    else:
        print('No command issued...')