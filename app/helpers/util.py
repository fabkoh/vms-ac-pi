def int_or_default(obj, default):
    '''util function to return a default value if obj cannot be converted to an int
    
    Args:
        obj (any): object to convert to int
        default (int): default int to return
        
    Returns:
        integer (int)
    '''
    try:
        return int(obj)
    except:
        return default