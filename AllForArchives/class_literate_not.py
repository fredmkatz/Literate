# class_literate.py
from typing import List, Dict, Any, Optional

from ldm.ldm_renderer import LDMRenderer
from ldm.ldm_validator import LDMValidator


class Literate:
    """
    Base class for all literate programming models.
    Provides common functionality for rendering and validation.
    """

    # Modified __init__ method for class_literate.py
    def __init__(self, name: str = None, description: str = None):
        print(f"\n=== INITIALIZING {self.__class__.__name__} ===")
        self.name = name
        self.description = description

        # Check if these import properly
        print("Importing renderer and validator...")
        try:
            from ldm.ldm_renderer import LDMRenderer

            print("LDMRenderer imported successfully")
        except Exception as e:
            print(f"Error importing LDMRenderer: {e}")

        try:
            from ldm.ldm_validator import LDMValidator

            print("LDMValidator imported successfully")
        except Exception as e:
            print(f"Error importing LDMValidator: {e}")

        # Create the renderer and validator
        try:
            from ldm.ldm_renderer import LDMRenderer

            self._renderer = LDMRenderer()
            print(f"Renderer created: {self._renderer}")
        except Exception as e:
            print(f"Error creating renderer: {e}")
            self._renderer = None

        try:
            from ldm.ldm_validator import LDMValidator

            self._validator = LDMValidator()
            print(f"Validator created: {self._validator}")
        except Exception as e:
            print(f"Error creating validator: {e}")
            self._validator = None

        # Check if _type is set properly
        _type = getattr(self, "_type", None)
        print(f"Object _type: {_type}")
        print("=== INITIALIZATION COMPLETE ===\n")

    def render_markdown(self) -> str:
        """Render the model as markdown"""
        return self._renderer.render_markdown(self)

    # Replace the validate method in the Literate class

    def validate(self) -> List[str]:
        """Validate the model"""
        print(f"\n=== VALIDATING {self.__class__.__name__} ===")

        # Ensure validator exists
        if not hasattr(self, "_validator") or self._validator is None:
            try:
                from ldm.ldm_validator import LDMValidator

                self._validator = LDMValidator()
                print(f"Created new validator in validate method: {self._validator}")
            except Exception as e:
                print(f"Failed to create validator: {e}")
                return [f"Failed to create validator: {str(e)}"]

        # Set the _type attribute if not already set
        if not hasattr(self, "_type"):
            self._type = self.__class__.__name__
            print(f"Set _type to: {self._type}")

        # Now validate
        print(
            f"Calling validator.validate with object type: {getattr(self, '_type', None)}"
        )
        try:
            errors = self._validator.validate(self)
            print(f"Validator returned {len(errors)} errors: {errors}")
            return errors
        except Exception as e:
            print(f"Exception during validation: {e}")
            import traceback

            traceback.print_exc()
            return [f"Validation failed with exception: {str(e)}"]

    # Replace the from_dict method in the Literate class in class_literate.py

    @classmethod
    def from_dict(cls, data_dict: Dict[str, Any]):
        """Create a model instance from a dictionary representation"""
        from ldm_object_creator import GenericObjectCreator
        import trials.Literate_01 as Literate_01

        creator = GenericObjectCreator(Literate_01)
        # print(f"Creating model from dictionary: {data_dict}")
        model = creator.create(data_dict)
        print(f"Created model: {model.__class__}")

        return model
