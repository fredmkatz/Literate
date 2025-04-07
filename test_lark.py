# test_lark.py
try:
    import lark
    print(f'Lark version: {lark.__version__}')
    print('Lark import successful!')
except ImportError as e:
    print(f'Import error: {e}')
    
    # Let's see what's in the lark-parser package
    try:
        import lark_parser
        print('Found as lark_parser instead')
    except ImportError:
        print('lark_parser not found either')
        
    # List all installed packages
    import pkg_resources
    print('Installed packages:')
    for pkg in pkg_resources.working_set:
        if 'lark' in pkg.key:
            print(f'  {pkg.key} {pkg.version}')
