import os 
import hashlib
import argparse
import struct
import re

def creare_archive(input_dir, extensions, archive_path):
    nr_file= 0
    with open(archive_path, 'w',encoding='utf-8' ) as archive: #deschidere fisier arhiva pt a putea scrie datele
        print(f"Calea directorului de intrare este: {input_dir}")
        for root, _, files in os.walk(input_dir):#_ rep ca se iau in considerare subdirectoarele, files fisierele din director
           # print(f"aici")
            for file in files:
               # print("ai")
                if any(file.endswith(ext) for ext in extensions):# any va returna true daca exista macar 1
                    print(f"Procesam fisierul: {file}")  # Afiseaza fiecare fisier procesat
                    file_path = os.path.join(root, file) 
                    relative_path = os.path.relpath(file_path, input_dir)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        nr_file += 1
                        print(f"Citirea fisierului {file} a avut loc, lungime continut: {len(content)}")
                    archive.write(f"PATH:{relative_path}\n")  # Scrie calea relativa
                    archive.write(f"SIZE:{len(content)}\n")   # Scrie dimensiunea con'inutului
                    archive.write("CONTENT:\n")              # Marcaj pentru inceputul con'inutului
                    archive.write(content)                   # Scrie con'inutul fisierului
                    archive.write("\nEND_OF_FILE\n")         # Marcaj pentru sfarsitul fisierului       
                    print(f"Includem in arhiva: {relative_path}, dimensiune: {len(content)} bytes")
        archive.write(f"\nTOTAL_FILES:{nr_file}\n")    
    print(f"Arhiva a fost creata la {archive_path}")
    print(f"Au fost scrise {nr_file} fisiere")


def slice_archive(archive_path, output_dir):
    print("aici")    
    os.makedirs(output_dir, exist_ok=True) #Creaza director
   # print(f"se va scrie in {output_dir}")
    #slice_path = r"C:\Users\Livia\Output\new\create.bin"  
    if not os.path.exists(archive_path):
       print(f"Eroare: {archive_path} nu exista.")
       return  
    slice_data = []
    current_size = 0
    slice_counter = 1
    with open(archive_path, 'r', encoding='utf-8') as archive:
      lines = archive.readlines()  
    ultima_linie = lines[-1].strip()   
    if "TOTAL_FILES:" in ultima_linie:
        nr_file = int(ultima_linie.split(":")[1].strip())  # Extragerea numarului
    else:
        nr_file =0
        print("Eroare: Nu s-a gasit linia cu TOTAL_FILES.")        
    #print(f"si aici")
    print(f"Numarul total de fisiere este: {nr_file}")
    num_characters =  sum(len(line) for line in lines[:-1]) 
    total_lines_size = sum(len(line.encode('utf-8')) for line in lines[:-1])  # Dimensiune pe biti
    nr_felii = 2 * nr_file  # Numarul dorit de felii
    max_slice_size =num_characters // nr_felii  # Dimensiune pentru o felie

    print(f"Dimensiunea totala a datelor: {total_lines_size} bytes")
    print(f"Dimensiunea maxima a unei felii: {max_slice_size} caractere")
    print(f"Numarul dorit de felii: {nr_felii}")

    for line in lines[:-1]:
      slice_data.append(line)
      current_size+=len(line)
      if current_size >= max_slice_size:
        slice_content = ''.join(slice_data)
        hash_name = hashlib.sha256(slice_content.encode('utf-8')).hexdigest()
        slice_path = os.path.join(output_dir, f"slice_{slice_counter}_{hash_name}.bin")
        # Scriem datele in felie
        with open(slice_path, 'w', encoding='utf-8') as slice_file:
           slice_file.write(slice_content)  
        print(f"Slice {slice_counter} creat: {slice_path}")
        slice_data = []  # Resetez datele pentru urmatoarea felie
        current_size = 0
        slice_counter +=1
        if slice_counter > nr_felii:
           break
        # Daca au ramas date de scris dupa procesarea tuturor fisierelor se pune intr-o ultima felie
    if slice_data:
          # hash_name = hashlib.sha256(b"".join(slice_data)).hexdigest()
            slice_content = ''.join(slice_data)
            hash_name = hashlib.sha256(slice_content.encode('utf-8')).hexdigest()
            slice_path = os.path.join(output_dir, f"slice_{slice_counter}_{hash_name}.bin")
            with open(slice_path, 'w', encoding = 'utf-8') as slice_file:
                #for data in slice_data:
                    slice_file.write(slice_content)
            print(f"Slice {slice_counter} creat: {slice_path}")
    print(f"Toate slice-urile au fost create în {output_dir}")

def restore_archive(slice_dir, output_archive_path): 
    #print("def")
    slices = os.listdir(slice_dir) #lista de slice uri
    #print("sortare")
    sorted_slices = sorted(slices,
                            key=lambda slice_name: int(re.search(r'slice_(\d+)_', slice_name).group(1)) 
                            if re.search(r'slice_(\d+)_', slice_name) 
                            else float('inf'))
    with open(output_archive_path,'wb')as archive: #creare fisierului arhiva 
        print("fisier arhiva")
        for slice_file in sorted_slices: #parcurge fiecare felie sortata
            slice_path = os.path.join(slice_dir,slice_file) #calea fiecarei felii
            with open(slice_path,'rb')as f: 
                archive.write(f.read()) #pune continutul in arhiva 
    print(f"Arhiva a fost restaurata la {output_archive_path}")


import argparse

parser = argparse.ArgumentParser(description="Slicer Tool")
subparsers = parser.add_subparsers(dest='command', required=True) #pentru cele 3 comenzi

# Subparser pentru "create"
create_parser = subparsers.add_parser('create', help="Creare arhiva")
create_parser.add_argument('input_dir', help="Directorul cu fisiere")
create_parser.add_argument('extensions', nargs='+', help="Extensiile de fisiere de inclus")
create_parser.add_argument('archive_path', help="Calea arhivei de iesire")

# Subparser pentru "slice"
slice_parser = subparsers.add_parser('slice', help="Felie arhiva")
slice_parser.add_argument('archive_path', help="Calea arhivei de intrare")
slice_parser.add_argument('output_dir', help="Directorul de iesire pentru felii")

# Subparser pentru "restore"
restore_parser = subparsers.add_parser('restore', help="Restaurare arhiva")
restore_parser.add_argument('slice_dir', help="Directorul cu felii")
restore_parser.add_argument('output_archive_path', help="Calea arhivei de iesire")

args = parser.parse_args()

# Interpretare comenzi
if args.command == 'create':
    print(f"Cream arhiva din directorul {args.input_dir} pentru extensiile {args.extensions}, la {args.archive_path}")
    creare_archive(args.input_dir, args.extensions,args.archive_path )
elif args.command == 'slice':
    print(f"Feliem arhiva {args.archive_path} in {args.output_dir}")
    slice_archive(args.archive_path, args.output_dir)
elif args.command == 'restore':
    print(f"Restauram arhiva din feliile {args.slice_dir} la {args.output_archive_path}") 
    restore_archive(args.slice_dir, args.output_archive_path)
