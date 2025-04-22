import sys

from LDMRecursive import LiterateParser, ParseError

def main():
    """Test the LiterateParser with a sample file."""
    try:
        # Parse command line arguments
        if len(sys.argv) < 2:
            print("Usage: python ldm_parser.py <filename>")
            sys.exit(1)
        
        filename = sys.argv[1]
        
        # Read input file
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Parse the input
        print(f"Parsing {filename}...")
        parser = LiterateParser(text)
        model = parser.parse()
        
        # Display the result
        print(f"Successfully parsed model!")
        if model.name:
            print(f"Model name: {model.name}")
        
        # Print class information
        print(f"Classes found: {len(model.classes)}")
        for cls in model.classes:
            print(f"  Class: {cls.name}")
            print(f"  - Attributes: {len(cls.attributes)}")
            if cls.dependents:
                print(f"  - Dependents: {', '.join(str(d) for d in cls.dependents)}")
            if cls.subtype_of:
                print(f"  - Subtype of: {', '.join(str(s) for s in cls.subtype_of)}")
            if cls.based_on:
                print(f"  - Based on: {', '.join(str(b) for b in cls.based_on)}")
        
        # Successful exit
        return 0
        
    except ParseError as e:
        print(f"Parse error: {str(e)}")
        return 1
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 2

if __name__ == "__main__":
    sys.exit(main())