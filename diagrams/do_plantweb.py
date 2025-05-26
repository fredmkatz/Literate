






if __name__ == '__main__':
    
    CONTENT = """
    actor Foo1
    boundary Foo2
    control Foo3
    entity Foo4
    database Foo5
    Foo1 -> Foo2 : To boundary
    Foo1 -> Foo3 : To control
    Foo1 -> Foo4 : To entity
    Foo1 -> Foo5 : To database
    """
    
    CONTENT2 = """puml
    nwdiag {
        network {
            Component;

            Component -- Literate;
            Component -- Subject;
            Component -- Class;
            Component -- AttributeSection;
            Component -- Attribute;

            Subject [description = "Domain entity"];
            Literate [description = "Core implementation"];
            Class [description = "Schema definition"];
            AttributeSection [description = "Property group"];
            Attribute [description = "Individual property"];
        }
    }
"""
    output_file = "PlantUML.png"
    
    outfile = render_puml(CONTENT2, format = "png", output_file=output_file)
    
    output_file = "PlantUML.svg"

    outfile = render_puml(CONTENT2, format = "svg", output_file=output_file)

