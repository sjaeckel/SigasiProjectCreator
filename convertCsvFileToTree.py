#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    :copyright: (c) 2008-2013 Sigasi
    :license: BSD, see LICENSE for more details.
"""

from optparse import OptionParser
import os
import platform
import subprocess
import csv

from SigasiProjectCreator import SigasiProjectCreator


def parse_csv_file(csv_file):
    entries = dict()
    with open(csv_file, 'rb') as f:
        reader = csv.reader(f, skipinitialspace=True)
        for row in reader:
            library = row[0].strip()
            path = row[1].strip()
            entries[path] = library
    return entries


def main():
    usage = """usage: %prog project-name csv-file [destination]

destination is the current directory by default
example: %prog filelist.csv 
"""
    parser = OptionParser(usage=usage)
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.error("incorrect number of arguments")

    project_name = args[0]
    csv_file = args[1]

    destination = os.getcwd()
    if len(args) > 2:
        destination = args[2]
        if not os.path.isdir(destination):
            parser.error("destination has to be a folder")

    entries = parse_csv_file(csv_file)

    def get_parts(pth):
        parts = []
        while True:
            pth, last = os.path.split(pth)
            if not last:
                break
            parts.append(last)
        return parts

    sigasi_project_file_creator = SigasiProjectCreator(project_name)
    sigasi_project_file_creator.unmap("/")

    linked_folders = dict()
    for path, library in entries.iteritems():
        abs_destination = os.path.abspath(destination)
        abs_path = os.path.abspath(path)
        relative_path = os.path.relpath(abs_path, abs_destination)
        if not relative_path.startswith(".."):
            sigasi_project_file_creator.add_mapping(relative_path, library)
        else:
            common_prefix = os.path.commonprefix([abs_path, abs_destination])
            eclipse_path = os.path.relpath(abs_path, common_prefix)
            directory_name = get_parts(eclipse_path)[-1]
            target = os.path.join(common_prefix, directory_name)

            linked_folders[directory_name] = target

            sigasi_project_file_creator.add_mapping(eclipse_path, library)

    # Adding custom items to libraries.
    # sigasi_project_file_creator.add_unisim("C:/xilinx/14.5/ISE_DS/ISE/vhdl/src/unisims")
    # sigasi_project_file_creator.add_unimacro("C:/xilinx/14.5/ISE_DS/ISE/vhdl/src/unimacro")

    def running_in_cyg_win():
        return platform.system().startswith("CYGWIN")

    def convert_cygwin_path(cygwin_path):
        cygwin_process = subprocess.Popen(['/usr/bin/cygpath', '--windows', cygwin_path], stdout=subprocess.PIPE)
        cygwin_location = cygwin_process.communicate()[0].rstrip()
        cygwin_location = cygwin_location.replace('\\', '/')
        return cygwin_location

    for folder, location in linked_folders.iteritems():
        if running_in_cyg_win():
            location = convert_cygwin_path(location)
        sigasi_project_file_creator.add_link(folder, location, 2)

    sigasi_project_file_creator.write(destination)

if __name__ == '__main__':
    main()
