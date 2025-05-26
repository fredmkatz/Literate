from AllToArchive.class_faculty import Faculty

# Markdown Renderer with simplified registration
class MarkdownRenderer(Faculty):
    """Markdown renderer for LDM classes"""
    
    def __init__(self, model_module="Literate_01"):
        """Initialize the markdown renderer"""
        print(f"Initializing MarkdownRenderer with model module: {model_module}")
        super().__init__("render", model_module)
        print("Classes are registered:")
        for cls in self.classes:
            print(f"Class: {cls}")
        # Register Component handler 
        if "Component" in self.classes:
            self.register_common_handler(self.classes["Component"], self.render_component)
        
        # Automatically register renderers
        self.register_renderers()
        print ("Renderers registered:")
            
    def render_component(self, obj):
        """Render component content (common functionality)"""
        result = ""
        if hasattr(obj, "elaboration") and obj.elaboration:
            result = "\n\t".join([p.render_markdown() for p in obj.elaboration])
        return result
    
    def register_renderers(self):
        """Register renderers for model classes"""
        # Register specific renderers for each class
        
        # LDM renderer
        @self.register()  # No target class needed - inferred from method name
        def render_ldm(self):
            result = f"# {self.name}\n\n"
            
            # Render subjects (parent handled automatically)
            if hasattr(self, "subjects"):
                for subject in self.subjects:
                    result += subject.render_markdown()
            return result
        
        # Subject renderer
        @self.register()
        def render_subject(self):
            result = f"{self.prefix} {self.name}\n\n"
            
            # Render classes (parent handled automatically)
            if hasattr(self, "classes"):
                for cls in self.classes:
                    result += cls.render_markdown()
            return result
        
        # Class renderer
        @self.register()
        def render_class(self):
            result = f"Class: {self.name}\n\n"
            
            # Render attributes (parent handled automatically)
            if hasattr(self, "attributes"):
                for attr in self.attributes:
                    result += attr.render_markdown()
            return result
        
        # Attribute renderer
        @self.register()
        def render_attribute(self):
            return f" Attribute: {self.name}\n\n"
        
        # Paragraph renderer
        @self.register()
        def render_paragraph(self):
            return self.content
        
 #####USAGE EXAMPLE#####
 
#  # Create and apply markdown renderer
# markdown = MarkdownRenderer("Literate_01")
# markdown.apply("markdown", "render_markdown")

# # Use the methods
# ldm = LDM(name="Example LDM")
# markdown_output = ldm.render_markdown()