__doc__ = """
Subir archivos al respaldo externo de la empresa, mediante el api de dropbox
Use:
   Multiples carpetas
   python dbxsync_files.py --folder '/tmp/xxx/' '/tmp/xxx1/' --dest '//Fuentes/' --token 'sf32134114ff2131241'
   Mutiples archivos
   python dbxsync_files.py --folder '/tmp/1.webm' '/tmp/2.webm' --dest '//Infraestructura/' --token 'sf32134114ff2131241'
"""
import argparse
#import contextlib
import datetime
import os
#import six
import sys
import time
#import unicodedata
import shutil
import dropbox
from dropbox.files import WriteMode
from dropbox.exceptions import ApiError, AuthError
from dropbox import DropboxOAuth2FlowNoRedirect

parser = argparse.ArgumentParser(description='Descarga y Actualiza Carpeta con Dropbox')
parser.add_argument('--carpetaLocal',dest="carpetaLocal",type=str,nargs='+',help='Carpeta Local FULLPATH')
parser.add_argument('--carpetaDropbox',dest='carpetaDropbox',nargs='+',help='Carpeta Dropbox FULLPATH')
parser.add_argument('--token',dest='token',nargs='+',help='Token')
args = parser.parse_args()
ocarpetaLocal = args.carpetaLocal[0]
ocarpetaDropbox = args.carpetaDropbox[0]
token = args.token[0]
if not ocarpetaLocal:
    sys.exit(2)
    print('Debe proveer una carpeta local')
if not ocarpetaDropbox:
    sys.exit(2)
    print('Debe proveer una carpeta de Dropbox')
if not token:
    sys.exit(2)
    print('Debe proveer un token')
    
dbx = dropbox.Dropbox(token)

def descargarCambios(carpetaLocal, carpetaDropbox):
    #print(carpetaLocal + " >> " + carpetaDropbox)
    for entry in dbx.files_list_folder(carpetaDropbox, include_deleted=True).entries:
        if (isinstance(entry, dropbox.files.DeletedMetadata)):
            path = carpetaLocal+entry.path_display
            path = path.replace(ocarpetaDropbox.lower(), "")
            while '/' in path:
                path = path.replace('/', '\\')

            #path = path.replace("\\sistemasamedida\\gruposignar\\infored","")
            if os.path.exists(path):
                #print(path)
                if (isinstance(entry, dropbox.files.FolderMetadata)):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                
                print("DELETE >> " + entry.path_display.replace(ocarpetaDropbox.lower(),""))
        elif (isinstance(entry, dropbox.files.FileMetadata) and not isinstance(entry, dropbox.files.DeletedMetadata)):
            #print("elemento: ")
            #print(entry.path_display.replace("/sistemasamedida/gruposignar/infored","SUBIR >>> "))
            #dbx.files_download_to_file(carpetaLocal, entry.path_display, rev=None)
            
            path = carpetaLocal+entry.path_display
            path = path.replace(ocarpetaDropbox.lower(), "")
            while '/' in path:
                path = path.replace('/', '\\')

            #path = path.replace("\\sistemasamedida\\gruposignar\\infored","")
            pathFile = path
            path = path.replace(entry.name,"")
                
            if not os.path.exists(path):
                os.makedirs(path)
                
            extensionesCompatibles = ".zip.xls.xlsx.html.htm.jpg.gif.js.css.pdf.asa.asp.txt"
            
            if entry.path_display[-3:] in extensionesCompatibles:
                
                if not os.path.exists(pathFile):
                    print("ADD >>> " + entry.path_display.replace(ocarpetaDropbox.lower(),""))
                    dbx.files_download_to_file(pathFile, entry.path_display)
                else:

                    mtime = os.path.getmtime(pathFile)
                    mtime_dt = datetime.datetime(*time.gmtime(mtime)[:6])
                    size = os.path.getsize(pathFile)                    
                    if (entry.size != size) and (entry.client_modified > mtime_dt):
                        print("UPDATE >>> " + entry.path_display.replace(ocarpetaDropbox.lower(),""))
                        dbx.files_download_to_file(pathFile, entry.path_display)
                    else:
                        print("NADA >>> " + entry.path_display.replace(ocarpetaDropbox.lower(),""))
        elif (isinstance(entry, dropbox.files.FolderMetadata) and not isinstance(entry, dropbox.files.DeletedMetadata)):
            #print("CARPETA >>> " + entry.path_display.replace(ocarpetaDropbox,""))
            #print("DESCARGAR CAMBIOS : " + carpetaLocal + " >> " + entry.path_display)
            descargarCambios(carpetaLocal,entry.path_display)
        else:
            print("NO SE!!!!")
    return "TODO OK"
print(ocarpetaLocal + " >> " + ocarpetaDropbox)
descargarCambios(ocarpetaLocal, ocarpetaDropbox)
#descargarCambios("c:\python\infored", '/sistemasAMedida/gruposignar/infored')


#dbx.close()
