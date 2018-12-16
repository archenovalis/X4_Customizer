'''
Place to test individual transforms.
Note: the newest tests tend to be near the top.
'''

from pathlib import Path

# Import all transform functions.
import Framework
from Plugins import *


Settings(
    path_to_x4_folder = r'C:\Steam\SteamApps\common\X4 Foundations',
    )


# Test the extension checker.
if 0:
    Check_Extension('test_mod')
if 0:
    # Alternatively, check everything (may take longer).
    Check_All_Extensions()

# Simple cat unpack, allowing errors.
if 0:
    Settings.allow_cat_md5_errors = True
    Cat_Unpack(
        source_cat_path = r'D:\X4\Pack',
        dest_dir_path   = r'D:\X4\UnPack',
        is_extension    = True
        )


# Slightly more complex cat unpack.
if 0:
    # Pick where to grab cats from.
    # Could also call this script from that directory and use relative
    #  paths for the cat file names.
    # Append the name of a cat file if wanting to unpack just one.
    cat_dir = Path(r'C:\Steam\SteamApps\common\X4 Foundations')

    # Pick the output folder. This script places it under the cat_dir.
    dest_dir_path = 'extracted'

    # Optional wildcard pattern to use for matching.
    include_pattern = ['*.xml','*.xsd','*.lua'] #,'*.xpl']
    exclude_pattern = None

    # Call the unpacker.
    Cat_Unpack(
        source_cat_path = cat_dir,
        #dest_dir_path   = cat_dir / dest_dir_path,
        dest_dir_path   = r'D:\X4_extracted_2',
        is_extension    = False,
        include_pattern = None,#include_pattern,
        exclude_pattern = exclude_pattern
        )


# Cat pack test.
if 0:
    # Pick where to grab files from.
    # Could also call this script from that directory and use relative
    # paths for the cat file names.
    dir_path = Path(r'C:\Steam\SteamApps\common\X4 Foundations\extensions\test_mod')

    # Optional wildcard pattern to use for matching.
    include_pattern = '*.xml'
    exclude_pattern = None

    # Name of the cat file.
    # For extensions, use prefix 'ext_' for patching game files, or
    # prefix 'subst_' for overwriting game files.
    cat_name = 'ext_01.cat'

    Cat_Pack(
        source_dir_path = dir_path,
        dest_cat_path   = dir_path / cat_name,
        include_pattern = include_pattern,
        exclude_pattern = exclude_pattern
        )

    

# Run diff patch test on whatever xml.
if 0:
    jobs_game_file = Load_File('libraries/jobs.xml')
    Framework.File_Manager.XML_Diff.Unit_Test(
        test_node      = jobs_game_file.Get_Root(), 
        num_tests      = 100, 
        edits_per_test = 5,
        rand_seed      = 1,
        )


# Call a single transform to test call machinery.
if 0:
    Adjust_Job_Count()


# Manual testing of cat reading.
if 0:
    # Test: open up a cat file, the one with text pages.
    cat09 = X4_Customizer.File_Manager.Cat_Reader.Cat_Reader(
        Settings.path_to_x4_folder / '09.cat')
    
    # Read the files from it.
    t44 = cat09.Read('t/0001-L044.xml')
    
    # Now try out the source reader.
    reader = X4_Customizer.File_Manager.Source_Reader.Source_Reader
    reader.Init()
    t44_game_file = reader.Read('t/0001-L044.xml')
    jobs_game_file = reader.Read('libraries/jobs.xml')
    
    # Write to a new cat file.
    binary = t44_game_file.Get_Binary()
    cat_dir = Settings.path_to_x4_folder / 'extensions' / 'X4_Customizer'
    if not cat_dir.exists():
        cat_dir.mkdir(parents = True)
    
    cat_writer = X4_Customizer.File_Manager.Cat_Writer.Cat_Writer(
        cat_path = cat_dir / 'ext_01.cat')
    cat_writer.Add_File(t44_game_file)
    cat_writer.Write()


print('Test done')