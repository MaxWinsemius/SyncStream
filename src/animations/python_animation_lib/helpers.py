def set_channel_prop(animation, prop_name, prop_value):
    """
    Helper function for setting attributes of all channels of an animation.
    The property value in the YAML may be a single value, or a list with length == len(sockets).
    The list items will then be added to the channels individually.
    If the value is a list, but of non-matching length, it will also be added as-is to all channels.
    """

    #TODO: check `if not prop_name == "colour"` to accidentally match situations where len(sockets) == 3 (=len(colour))
    if prop_name == "colour" and len(prop_value) == 3:
        for ch in animation.channels:
            setattr(ch, prop_name, prop_value)
    
    elif type(prop_value) in (list, tuple) and not len(prop_value) == len(animation.channels): #too lazy to figure out what the yaml parser returns
        for ch, ls in zip(animation.channels, prop_value):
            setattr(ch, prop_name, ls)
    
    else:
        for ch in animation.channels:
            setattr(ch, prop_name, prop_value)