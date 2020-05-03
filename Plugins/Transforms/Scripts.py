
from fnmatch import fnmatch
from lxml.etree import Element
from Framework import Transform_Wrapper, Load_File, Load_Files, Plugin_Log
from .Support import Standardize_Match_Rules
from .Support import XML_Multiply_Int_Attribute
from .Support import XML_Multiply_Float_Attribute

__all__ = [
    'Increase_AI_Script_Waits',
    'Adjust_OOV_Damage',
    ]


@Transform_Wrapper()
def Increase_AI_Script_Waits(
        multiplier = 2, 
        seta_multiplier = 4,
        max_wait = 15,
        filter = '*',
        include_extensions = False,
        skip_combat_scripts = False,
        ):
    '''
    Increases wait times in ai scripts, to reduce their background load
    and improve performance.  Waits under "visible" attention will
    not be modified. Expected to have high impact on fps, at some
    cost of ai efficiency.

    * multiplier
      - Float, how much to multiply wait times by. Default is 2.
    * seta_multiplier
      - Float, alternate multiplier to apply if the player
        is in SETA mode. Default is 4.
      - Eg. if multiplier is 2 and seta_multiplier is 4, then waits will
        be 2x longer when not in SETA, 4x longer when in SETA.
    * max_wait
      - Float, optional, the longest wait that this multiplier can achieve,
        in seconds.
      - Defaults to 15.
      - If the original wait is longer than this, it will be unaffected.
    * filter
      - String, possibly with wildcards, matching names of ai scripts to
        modify; default is plain '*' to match all aiscripts.
      - Example: "*trade.*" to modify only trade scripts.
    * include_extensions
      - Bool, if True then aiscripts added by extensions are also modified.
      - Defaults False.
    * skip_combat_scripts
      - Bool, if True then scripts which control OOS damage application
        will not be modified. Otherwise, they are modified and their
        attack strength per round is increased to match the longer wait times.
      - Defaults False.
    '''
    
    # Just ai scripts; md has no load.
    aiscript_files = Load_Files(f"{'*' if include_extensions else ''}aiscripts/{filter}.xml")

    # Set up the string with the multiplication.
    mult_str = f"(if player.timewarp.active then {seta_multiplier} else {multiplier})"
    
    for game_file in aiscript_files:
        xml_root = game_file.Get_Root()
        file_name = game_file.name.replace('.xml','')
        
        # Find any get_attack_strength nodes, used in OOS combat.
        attack_strength_nodes = xml_root.xpath(".//get_attackstrength")
        # If there are any, and not modifying combat scripts, skip.
        if attack_strength_nodes and skip_combat_scripts:
            continue

        # Find all waits.
        nodes = xml_root.xpath(".//wait")
        if not nodes:
            continue

        # Find any waits under visible attention as well.
        # TODO: are there other ways visible attention is often specified?
        visible_waits = xml_root.xpath('.//attention[@min="visible"]//wait')

        for node in nodes:
            # Skip if visible.
            if node in visible_waits:
                continue

            for attr in ['min','max','exact']:
                orig = node.get(attr)
                if not orig:
                    continue

                # This will get the orig value, the orig value multiplied
                # with a ceiling, and take the max.
                new = f'[{orig}, [{max_wait}s, ({orig})*{mult_str}].min].max'
                node.set(attr, new)

        # Adjust attack strength to account for the timing change.
        for node in attack_strength_nodes:
            # For now, assume the waits were fully multiplied, and didn't
            # cap out at max_wait. Combat scripts appear to use a 1s
            # period (since attack_strength is dps), so this shouldn't
            # be an issue.

            # This can have up to 5 output values, that all need the
            # same multiplication.
            # A unified result is in a 'result' attribute.
            # Specific damages (shield, hull, etc.) are in a 'result'
            # subnode.
            # Gather the names of capture vars.
            out_vars = []

            if node.get('result'):
                out_vars.append(node.get('result'))
            result_subnode = node.find('./result')

            if result_subnode != None:
                for attr in ['hullshield','hullonly','shieldonly','hullnoshield']:
                    varname = result_subnode.get(attr)
                    if varname:
                        out_vars.append(varname)

            # Add in set_value nodes to multiply each of these.
            for varname in out_vars:
                new_node = Element('set_value',
                            name = varname,
                            exact = f'{varname} * {mult_str}')
                node.addnext(new_node)
                # lxml can mess up node id tails, so fix it.
                if new_node.tail != None:
                    assert node.tail == None
                    node.tail = new_node.tail
                    new_node.tail = None
                    
        game_file.Update_Root(xml_root)
                    
    return


@Transform_Wrapper()
def Adjust_OOV_Damage(multiplier):
    '''
    Adjusts all out-of-vision damage-per-second by a multiplier. For instance,
    if OOV combat seems to run too fast, it can be multiplied by 0.5 to
    slow it down by half.
    
    * multiplier
      - Float, how much to multiply damage by.
    '''
    # The code for this is similar to what was done above, just split off.
    # If the two transforms are used together, it's probably okay, will
    # just have a few extra cheap script instructions.
    
    aiscript_files = Load_Files(f"*aiscripts/*.xml")
    
    for game_file in aiscript_files:
        xml_root = game_file.Get_Root()
        file_name = game_file.name.replace('.xml','')
        
        # Find any get_attack_strength nodes, used in OOS combat.
        nodes = xml_root.xpath(".//get_attackstrength")
        if not nodes:
            continue

        for node in nodes:

            # Gather the names of capture vars.
            out_vars = []
            if node.get('result'):
                out_vars.append(node.get('result'))

            result_subnode = node.find('./result')
            if result_subnode != None:
                for attr in ['hullshield','hullonly','shieldonly','hullnoshield']:
                    varname = result_subnode.get(attr)
                    if varname:
                        out_vars.append(varname)

            # Add in set_value nodes to multiply each of these.
            for varname in out_vars:
                new_node = Element('set_value',
                            name = varname,
                            exact = f'{varname} * {multiplier}')
                node.addnext(new_node)
                # lxml can mess up node id tails, so fix it.
                if new_node.tail != None:
                    assert node.tail == None
                    node.tail = new_node.tail
                    new_node.tail = None
                    
        game_file.Update_Root(xml_root)

    return