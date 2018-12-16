'''
Main function for the X4_Customizer.
'''
import os
import sys
from pathlib import Path
import argparse

# To support packages cross-referencing each other, set up this
# top level as a package, findable on the sys path.
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.append(str(parent_dir))
# To support easy control script naming, add the Scripts folder to
# the search path, but put it at the end (to reduce interference
# if the user wants to import from their call location).
scripts_dir = parent_dir / 'Scripts'
if str(scripts_dir) not in sys.path:
    sys.path.append(str(scripts_dir))

import Framework


def Run(*args):
    '''
    Run the customizer.
    This expect a single argument: the name of the .py file to load
    which specifies file paths and the transforms to run. Some other
    command line args supported.  Excess args will be placed in
    sys.args for called script to argparse if desired.
    '''
    
    # Rename the settings for convenience.
    Settings = Framework.Settings
    
    # Set up command line arguments.
    argparser = argparse.ArgumentParser(
        description='Main function for running X4 Customizer version {}.'.format(
            Framework.Change_Log.Get_Version()
            ),
        # Special setting to add default values to help messages.
        # -Removed; doesn't work on positional args.
        #formatter_class = argparse.ArgumentDefault_ScriptsHelpFormatter,

        # To better support nested scripts doing their own argparsing,
        #  prevent abbreviation support at this level.
        allow_abbrev = False,
        )

    # Set this to default to None, which will be caught manually.
    argparser.add_argument(
        'control_script',
        default = 'Default_Script',
        # Consume 0 or 1 argument.
        # This prevents an error message when an arg not given,
        # and the default is used instead.
        nargs = '?',
        help =  'Python control script which will specify settings and'
                ' plugins to run; path may be given relative to the Scripts'
                ' folder; .py extension is optional; defaults to running'
                ' Scripts/Default_Script.py'
               )
    
    # Flag to clean out old files.
    argparser.add_argument(
        '-clean', 
        action='store_true',
        help = 'Cleans out any files created on the prior run,'
               ' and reverts any file renamings back to their original names.'
               ' Files in the user source folder will be moved to the game'
               ' folders without modifications.'
               ' Still requires a user_transform file which specifies'
               ' the necessary paths, but transforms will not be run.')
    
    argparser.add_argument(
        '-dev', 
        action='store_true',
        help =  'Enables developer mode, which makes some changes to'
                ' exception handling.')
    
    argparser.add_argument(
        '-quiet', 
        action='store_true',
        help =  'Hides some status messages.')
    
    argparser.add_argument(
        '-test', 
        action='store_true',
        help =  'Performs a test run of the transforms, behaving like'
                ' a normal run but not writing out modified files.')
    
    argparser.add_argument(
        '-argpass', 
        action='store_true',
        help =  'Indicates the control script has its own arg parsing;'
                ' extra args and "-h" are passed through sys.argv.')
    
    # Capture leftover args.
    # Note: when tested, this appears to be buggy, and was grabbing
    # "-dev" even though that has no ambiguity; parse_known_args
    # works better.
    #argparser.add_argument('args', nargs=argparse.REMAINDER)
    
    # Parsing behavior will change depending on if args are being
    # passed downward.
    if not '-argpass' in args:
        # Do a normal arg parsing.
        args = argparser.parse_args(args)

    else:
        # Pick out the -h flag, so help can be printed in the
        # control script instead of here.
        pass_help_arg = False
        if '-h' in args:
            pass_help_arg = True
            # Need to swap from tuple to list to remove an item.
            args = list(args)
            args.remove('-h')

        # Do a partial parsing.
        args, remainder = argparser.parse_known_args(args)

        # Put the remainder in sys.argv so called scripts can use it;
        # these should go after the first argv (always the called script name,
        # eg. Main.py).
        sys.argv = [sys.argv[0]] + remainder
        # Add back in the -h flag.
        if pass_help_arg:
            sys.argv.append('-h')


    # Convenience flag for when the default script is in use.
    using_default_script = args.control_script == 'Default_Script'

    # Convert the script to a Path, for convenience.
    args.control_script = Path(args.control_script)
    
    # Add the .py extension if needed.
    if args.control_script.suffix != '.py':
        args.control_script = args.control_script.with_suffix('.py')

    # If the given script isn't found, try finding it in the scripts folder.
    # Only support this switch for relative paths.
    if not args.control_script.exists() and not args.control_script.is_absolute():
        alt_path = scripts_dir / args.control_script
        if alt_path.exists():
            args.control_script = alt_path


    # Handle if the script isn't found.
    if not args.control_script.exists():
        # If the default script is in use, Main may have been called with
        # no args, which case print the argparse help.
        if using_default_script:
            argparser.print_help()

        # Follow up with an error on the control script name.
        print('Error: {} not found.'.format(args.control_script))

        # Print some extra help text if the user tried to run the default
        #  script from the bat file.
        if using_default_script:
            # Avoid word wrap in the middle of a word by using an explicit
            #  newline.
            print('For new users, please open Scripts/'
                  'Default_Script_template.py\n'
                  'for first time setup instructions.')
        return


    # Add the script location to the search path, so it can include
    # other scripts at that location.
    # This will often just by the Scripts folder, which is already in
    # the sys.path, but for cases when it is not, put this path
    # early in the search order.
    control_script_dir = args.control_script.parent
    if str(control_script_dir) not in sys.path:
        sys.path.insert(0, str(control_script_dir))
    
        
    # Handle other args.
    if args.quiet:
        Settings.verbose = False

    if args.clean:
        print('Enabling cleanup mode; transforms will be skipped.')
        Settings.skip_all_transforms = True

    if args.dev:
        print('Enabling developer mode.')
        Settings.developer = True

    if args.test:
        print('Performing test run.')
        # This uses the disable_cleanup flag.
        Settings.disable_cleanup_and_writeback = True
                

    print('Calling {}'.format(args.control_script))
    try:
        # Attempt to load the module.
        # This will kick off all of the transforms as a result.
        import importlib        
        module = importlib.machinery.SourceFileLoader(
            # Provide the name sys will use for this module.
            # Use the basename to get rid of any path, and prefix
            #  to ensure the name is unique (don't want to collide
            #  with other loaded modules).
            'control_script_' + args.control_script.name.replace(' ','_'), 
            # Just grab the name; it should be found on included paths.
            str(args.control_script)
            ).load_module()
        
        #print('Run complete')    

    except Exception as ex:
        # Make a nice message, to prevent a full stack trace being
        #  dropped on the user.
        print('Exception of type "{}" encountered.\n'.format(
            type(ex).__name__))
        ex_text = str(ex)
        if ex_text:
            print(ex_text)
            
        # Close the plugin log safely (in case of raising another
        #  exception).
        Framework.Common.Logs.Plugin_Log.Close()

        # In dev mode, reraise the exception.
        if Settings.developer:
            raise ex
        #else:
        #    print('Enable developer mode for exception stack trace.')
        
    return

if __name__ == '__main__':
    Run(*sys.argv[1:])