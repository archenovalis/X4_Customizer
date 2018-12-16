'''
Change Log:
 * 0.9
   - Initial version, quick adaption of X3_Customizer for X4.
   - Added first transform, Adjust_Job_Count.
 * 0.9.1
   - Major framework development.
   - Settings overhauled for X4.
   - Source_Reader overhauled, now finds and pulls from extensions.
   - Xml diff patch support added for common operations, merging extensions
     and base files prior to transforms. Pending further debug.
 * 0.9.2
   - Fix for when the user content.xml isn't present.
 * 0.9.3
   - Major development of diff patch generation, now using close to
     minimal patch size instead of full tree replacement, plus
     related debug of the patch application code.
   - Framework largely feature complete, except for further debug.
 * 0.9.4
   - Applied various polish: documentation touchup, gathered misc
     file_manager functions into a class, etc.
   - Added dependency nodes to the output extension.
 * 0.10
   - Major reorganization, moving transforms into a separate Plugins
     package that holds runtime script imports.
   - Added utilities for simple cat operations.
   - Added Print_Weapon_Stats.
 * 0.10.1
   - Added workaround for a bug in x4 catalogs that sometimes use
     an incorrect empty file hash; also added an optional setting to
     allow hash mismatches to support otherwise problematic catalogs.
 * 0.10.2
   - Bug fix in cat unpacker.
 * 0.11
   - Added plugins Check_Extension, Check_All_Extensions.
   - Added passthrough argparse support, along with command line callable
     scripts for extension check and cat pack/unpack.
   - Swapped the default script from User_Transforms to Default_Script.
 * 0.11.1
   - Added support for case insensitive path matching, instead of
     requiring a match to the catalogs.
'''
# Note: changes moved here for organization, and to make them easier to
# break out during documentation generation.

def Get_Version():
    '''
    Returns the highest version number in the change log,
    as a string, eg. '3.4.1'.
    '''
    # Traverse the docstring, looking for ' *' lines, and keep recording
    #  strings as they are seen.
    version = ''
    for line in __doc__.splitlines():
        if not line.startswith(' *'):
            continue
        version = line.split('*')[1].strip()
    return version