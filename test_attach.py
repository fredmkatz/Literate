# Add this temporary diagnostic code to your script
import ldm.Literate_01 as Literate_01

# Check if the render_markdown method exists on the class definition
print("LiterateModel class has render_markdown:", hasattr(Literate_01.LiterateModel, "render_markdown"))

# Create a simple instance directly
test_ldm = Literate_01.LiterateModel(name="Test")

# Check if the instance has the method
print("LiterateModel instance has render_markdown:", hasattr(test_ldm, "render_markdown"))

# Add a method directly to the class definition
def test_render(self):
    return f"Test render for {self.name}"

Literate_01.LiterateModel.test_render = test_render

# Create another instance
test_ldm2 = Literate_01.LiterateModel(name="Test2")

# Check if the new instance has the method
print("Second LiterateModel instance has test_render:", hasattr(test_ldm2, "test_render"))

# Try calling it
print("Output:", test_ldm2.test_render())