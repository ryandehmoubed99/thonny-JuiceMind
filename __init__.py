import os.path
from thonny import get_workbench
from thonny.ui_utils import select_sequence


def load_plugin():
    #image_path = os.path.join(os.path.dirname(__file__), "../DrPhil.png")
    
    
    get_workbench().add_command("program_DrPhil", "tools", "Send current script to DrPhil",
                                default_sequence=select_sequence("<Control-e>", "<Command-e>"),
                                group=120,
                                caption="Touch me",
                                include_in_toolbar=True)

