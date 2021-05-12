import logging
import os
import re
from thonny import get_workbench, get_runner
from thonny.ui_utils import scale
from thonny.ui_utils import select_sequence

import logging
import threading
import time



#Don't undestand what these do

DESKTOP_SESSION = os.environ.get("DESKTOP_SESSION", "_")
CONFIGURATION_PATH = os.path.join(
    os.path.expanduser("~"), ".config/lxsession", DESKTOP_SESSION, "desktop.conf"
)

GLOBAL_CONFIGURATION_PATH = os.path.join("/etc/xdg/lxsession", DESKTOP_SESSION, "desktop.conf")

logger = logging.getLogger(__name__)


#Global variables
esp32_boolean = False
startup_theme = "JuiceMind-Theme"


def pix():

    #Flexibility to change the background to a color of our choice
    MAIN_BACKGROUND = "#ededed"

    #This is for different scroll arrows
    detail_bg = "#d0d0d0"
    detail_bg2 = "#cfcdc8"

    #Initializes the res directory    
    res_dir = os.path.join(os.path.dirname(__file__), "res")
    scrollbar_button_settings = {}
    
    
    #Sets different aspects of the scrollbar
    for direction, element_name in [
        ("up", "Vertical.Scrollbar.uparrow"),
        ("down", "Vertical.Scrollbar.downarrow"),
        ("left", "Horizontal.Scrollbar.leftarrow"),
        ("right", "Horizontal.Scrollbar.rightarrow"),
    ]:
        # load the image
        img_name = "scrollbar-button-" + direction
        for suffix in ["", "-insens"]:
            get_workbench().get_image(
                os.path.join(res_dir, img_name + suffix + ".png"), img_name + suffix
            )

        scrollbar_button_settings[element_name] = {
            "element create": (
                "image",
                img_name,
                ("!disabled", img_name),
                ("disabled", img_name + "-insens"),
            )
        }

    settings = {
        ".": {"configure": {"background": MAIN_BACKGROUND}},
        "Toolbutton": {
            "configure": {"borderwidth": 1},
            "map": {
                "relief": [("disabled", "flat"), ("hover", "groove"), ("!hover", "flat")],
                "background": [
                    ("disabled", MAIN_BACKGROUND),
                    ("!hover", MAIN_BACKGROUND),
                    ("hover", "#ffffff"),
                ],
            },
        },
        "Treeview.Heading": {
            "configure": {
                "background": "#f0f0f0",
                "foreground": "#808080",
                "relief": "flat",
                "borderwidth": 1,
            },
            "map": {"foreground": [("active", "black")]},
        },
        "TNotebook.Tab": {
            "map": {"background": [("!selected", detail_bg), ("selected", MAIN_BACKGROUND)]}
        },
        "ButtonNotebook.TNotebook.Tab": {
            "map": {
                "background": [("!selected", detail_bg), ("selected", MAIN_BACKGROUND)],
                "padding": [
                    ("selected", [scale(4), scale(2), scale(4), scale(3)]),
                    ("!selected", [scale(4), scale(2), scale(4), scale(3)]),
                ],
            }
        },
        "TScrollbar": {
            "configure": {
                "gripcount": 0,
                "borderwidth": 0,
                "padding": scale(1),
                "relief": "solid",
                "background": "#9e9e9e",
                "darkcolor": "#d6d6d6",
                "lightcolor": "#d6d6d6",
                "bordercolor": "#d6d6d6",
                "troughcolor": "#d6d6d6",
                "arrowsize": scale(1),
                "arrowcolor": "gray",
            },
            "map": {"background": [], "darkcolor": [], "lightcolor": []},
        },
        # Padding allows twaking thumb width
        "Vertical.TScrollbar": {
            "layout": [
                (
                    "Vertical.Scrollbar.trough",
                    {
                        "sticky": "ns",
                        "children": [
                            ("Vertical.Scrollbar.uparrow", {"side": "top", "sticky": ""}),
                            ("Vertical.Scrollbar.downarrow", {"side": "bottom", "sticky": ""}),
                            (
                                "Vertical.Scrollbar.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Vertical.Scrollbar.thumb",
                                            {"expand": 1, "sticky": "nswe"},
                                        )
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ]
        },
        "Horizontal.TScrollbar": {
            "layout": [
                (
                    "Horizontal.Scrollbar.trough",
                    {
                        "sticky": "we",
                        "children": [
                            ("Horizontal.Scrollbar.leftarrow", {"side": "left", "sticky": ""}),
                            ("Horizontal.Scrollbar.rightarrow", {"side": "right", "sticky": ""}),
                            (
                                "Horizontal.Scrollbar.padding",
                                {
                                    "sticky": "nswe",
                                    "children": [
                                        (
                                            "Horizontal.Scrollbar.thumb",
                                            {"expand": 1, "sticky": "nswe"},
                                        )
                                    ],
                                },
                            ),
                        ],
                    },
                )
            ],
            "map": {
                # Make disabled Hor Scrollbar invisible
                "background": [("disabled", "#d6d6d6")],
                "troughcolor": [("disabled", "#d6d6d6")],
                "bordercolor": [("disabled", "#d6d6d6")],
                "darkcolor": [("disabled", "#d6d6d6")],
                "lightcolor": [("disabled", "#d6d6d6")],
            },
        },
        "TCombobox": {"configure": {"arrowsize": scale(10)}},
        "Menubar": {
            "configure": {
                "background": MAIN_BACKGROUND,
                "relief": "flat",
                "activebackground": "#ffffff",
                "activeborderwidth": 0,
            }
        },
        "Menu": {
            "configure": {
                "background": "#ffffff",
                "relief": "flat",
                "borderwidth": 1,
                "activeborderwidth": 0,
                # "activebackground" : bg, # updated below
                # "activeforeground" : fg,
            }
        },
        "Tooltip": {
            "configure": {
                "background": "#808080",
                "foreground": "#ffffff",
                "borderwidth": 0,
                "padx": 10,
                "pady": 10,
            }
        },
        "Tip.TLabel": {"configure": {"background": detail_bg2, "foreground": "black"}},
        "Tip.TFrame": {"configure": {"background": detail_bg2}},
        "OPTIONS": {"configure": {"icons_in_menus": False, "shortcuts_in_tooltips": False}},
    }

    settings.update(scrollbar_button_settings)

    # try to refine settings according to system configuration. Come back to this feature only if we want to modify the overall fonts manually.
    """Note that fonts are set globally, 
    ie. all themes will later inherit these"""
    update_fonts()

    for path in [GLOBAL_CONFIGURATION_PATH, CONFIGURATION_PATH]:
        if os.path.exists(path):
            with open(path) as fp:
                try:
                    for line in fp:
                        if "sGtk/ColorScheme" in line:
                            if "selected_bg_color" in line:
                                bgr = re.search(
                                    r"selected_bg_color:#([0-9a-fA-F]*)", line, re.M
                                ).group(
                                    1
                                )  # @UndefinedVariable
                                color = "#" + bgr[0:2] + bgr[4:6] + bgr[8:10]
                                if is_good_color(color):
                                    settings["Menu"]["configure"]["activebackground"] = color
                            if "selected_fg_color" in line:
                                fgr = re.search(
                                    r"selected_fg_color:#([0-9a-fA-F]*)", line, re.M
                                ).group(
                                    1
                                )  # @UndefinedVariable
                                color = "#" + fgr[0:2] + fgr[4:6] + fgr[8:10]
                                if is_good_color(color):
                                    settings["Menu"]["configure"]["activeforeground"] = color
                except Exception as e:
                    logger.error("Could not update colors", exc_info=e)

    return settings


def is_good_color(s):
    return bool(re.match("^#[0-9a-fA-F]{6}$", s))


def pix_dark():
    update_fonts()
    return {}


def update_fonts():
    from tkinter import font

    options = {}
    for path in [GLOBAL_CONFIGURATION_PATH, CONFIGURATION_PATH]:
        if os.path.exists(path):
            try:
                with open(path) as fp:
                    for line in fp:
                        if "sGtk/FontName" in line:
                            result = re.search(
                                r"=([^0-9]*) ([0-9]*)", line, re.M
                            )  # @UndefinedVariable
                            family = result.group(1)
                            options["size"] = int(result.group(2))

                            if re.search(r"\bBold\b", family):
                                options["weight"] = "bold"
                            else:
                                options["weight"] = "normal"

                            if re.search(r"\bItalic\b", family):
                                options["slant"] = "italic"
                            else:
                                options["slant"] = "roman"

                            options["family"] = family.replace(" Bold", "").replace(" Italic", "")
            except Exception as e:
                logger.error("Could not update fonts", exc_info=e)

    if options:
        for name in ["TkDefaultFont", "TkMenuFont", "TkTextFont", "TkHeadingFont"]:
            font.nametofont(name).configure(**options)


'''

def disable_MCU():

    print(get_workbench().get_option("run.backend_name"))

    #Disable button when the MCU is selected
    if (get_workbench().get_option("run.backend_name") == "ESP8266"):
        return False
    
    #Don't disable if you are on normal interpreter
    else:
        return True


def disable_computer():

    #Disable button when computer is selected
    if (get_workbench().get_option("run.backend_name") == "SameAsFrontend"):
        return False
    else:
        return True



#Callback Function to change interpreter to MicroPython
def switch_to_microPython():

    
    #Configure the default interpreter value to be an ESP32
    get_workbench().set_option("run.backend_name", "ESP8266")


    #Restart backend to implement changes with the new interpreter
    get_runner().restart_backend(False)






#Callback function to change interpreter to regular Python on computer
def switch_to_python():

    
    #Configure the default interpreter value to be an ESP32
    get_workbench().set_option("run.backend_name", "SameAsFrontend")

 
    #Restart backend to implement changes with the new interpreter
    get_runner().restart_backend(False)

'''


#index of current search of USB devices
index = 0

#Initialize MicroPython proxy to be initially None
proxy = None

#Thonny establishes a connection with the MCU once the connection boolean changes from True to None
prev_connection = None



#Callback function that aims at checking if current USB is the correct USB port.
def connect_device():


    proxy =  get_workbench().get_backends()["ESP8266"].proxy_class

    #If nothing is connected don't do anything -> Maybe in the future make a pop-up that says to plug-in a device


    #There is only one port to connect to
    if(len(proxy._detect_potential_ports()) == 1): 

        #List the potential USB name
        USB_name = proxy._detect_potential_ports()[index][0]

        #Establish a serial connection with that USB
        establish_serial_connection(USB_name)

        

    #Multiple USB ports are connected. We are assuming that the only additional USB that can be listed in the window is going to be the SLAB port 
    elif(len(proxy._detect_potential_ports()) > 1): 

        USB_name = ""

        for i in range(len(proxy._detect_potential_ports())):

            temp_USB = proxy._detect_potential_ports()[i][0]

            if "SLAB" in temp_USB:

                USB_name = temp_USB
                break

    
        establish_serial_connection(USB_name)


    #Otherwise don't do anything to connect

    '''
    global index
    global proxy

    #Only enable device connection if the ESP32 mode is selected
    if (get_workbench().get_option("run.backend_name") ==  "ESP32"):

        proxy = get_workbench().get_backends()["ESP32"].proxy_class

        #There is more than one port to connect to
        if (len(proxy._detect_potential_ports()) > 0):

            #Establish a serial connection with a specific serial port
            USB_name = proxy._detect_potential_ports()[index][0]
            
            #Increment the index
            index = index + 1

            #Establish a serial connection
            establish_serial_connection(USB_name)

            
    '''

def establish_serial_connection(USB_name):

    #Change the setting for the USB connection 
    get_workbench().set_option("ESP8266.port", USB_name)

    #Restart the backend to establish changes 
    get_runner().restart_backend(False)



def test_connection():

    toolbar_button = get_workbench().get_toolbar_button("connect_button")
    res_dir = os.path.join(os.path.dirname(__file__), "res")
    img2 = None

    

    #If the current interpreter is the computer Python interpreter, make the image disabled and transparent.
    if (get_workbench().get_option("run.backend_name") ==  "SameAsFrontend"):

        microcontroller_selected_image = os.path.join(res_dir, "transparent_background.png")
        img2 = get_workbench().get_image(microcontroller_selected_image)
    
        toolbar_button.configure(image=img2)
        toolbar_button.image = img2

        #Change the image type to be empty
        return False


    #If the interpreter is ESP8266 and it is connected, make the image disabled and say that it is connected
    elif ((get_workbench().get_option("run.backend_name") ==  "ESP8266" and get_runner()._cmd_interrupt_enabled())):


        microcontroller_selected_image = os.path.join(res_dir, "connected-button.png")
        img2 = get_workbench().get_image(microcontroller_selected_image)
    
        toolbar_button.configure(image=img2)
        toolbar_button.image = img2

        return False

    
    #If the interpreter is ESP8266 and it is connected, make the image enabled and display the connected button.
    else:

        microcontroller_selected_image = os.path.join(res_dir, "connect.png")
        img2 = get_workbench().get_image(microcontroller_selected_image)
    
        toolbar_button.configure(image=img2)
        toolbar_button.image = img2

        return True


#Used for adding spacing between the buttons
def always_disabled():

    #Disable button when computer is selected.
    return False



#Used for the toggle bewteen MicroPython and regular Python.
def always_enabled():

    #Enable the button when computer is selected.
    return True



def toggle_python():
    

    toolbar_button = get_workbench().get_toolbar_button("toggle_python")
    res_dir = os.path.join(os.path.dirname(__file__), "res")
    img2 = None


    #Currently Computer is selected -> Switch to the Microcontroller interpreter
    if (get_workbench().get_option("run.backend_name") ==  "SameAsFrontend"):
    

        microcontroller_selected_image = os.path.join(res_dir, "MCU_selected.png")
        img2 = get_workbench().get_image(microcontroller_selected_image)
        
        #Change the backend to ESP8266
        get_workbench().set_option("run.backend_name", "ESP8266")

        #Restart the backend to establish changes
        get_runner().restart_backend(False)
    

    #Currently Microcontroller is selected -> Switch to the computer interpreter
    else:
    
    
        computer_selected_image = os.path.join(res_dir, "computer_selected.png")
        img2 = get_workbench().get_image(computer_selected_image)
       
        #Change the backend to Regular Python Interpreter
        get_workbench().set_option("run.backend_name", "SameAsFrontend")

        #Restart the backend to establish changes
        get_runner().restart_backend(False)

        
    toolbar_button.configure(image=img2)
    toolbar_button.image = img2




    '''
    global prev_connection
    global index
    global proxy


    #Check if the microcontroller is connected at any point in time
    if (get_workbench().get_option("run.backend_name") ==  "ESP32" and get_runner()._cmd_interrupt_enabled()): 

        #True -> Stays true the entire time        
        
        #Connect an MCU
        prev_connection = get_runner()._cmd_interrupt_enabled()

        return False

    #Check the previous state that it was connected.
    elif (get_runner()._cmd_interrupt_enabled() == None and prev_connection == True and proxy != None):

        #Try connecting again with a different USB port
        if(len(proxy._detect_potential_ports()) > 1 and index < len(proxy._detect_potential_ports())):

            USB_name = proxy._detect_potential_ports()[index][0]
            index = index + 1
            prev_connection = get_runner()._cmd_interrupt_enabled()
            establish_serial_connection(USB_name)
            return False
            
        else:

            #Set pressed button == False
            prev_connection = None
            index = 0
            return True

    else:

        prev_connection = None
        return True


    '''

def load_plugin():


    #No idea what the screenwidth condition does. I don't think it increases the screen size
    if get_workbench().get_ui_mode() == "simple" and get_workbench().winfo_screenwidth() >= 1280:
        images = {
            "run-current-script": "media-playback-start48.png",
            "stop": "process-stop48.png",
            "new-file": "document-new48.png",
            "open-file": "open_file.png",
            "save-file": "document-save48.png",
            "debug-current-script": "debug-run48.png",
            "step-over": "debug-step-over48.png",
            "step-into": "debug-step-into48.png",
            "step-out": "debug-step-out48.png",
            "run-to-cursor": "debug-run-cursor48.png",
            "tab-close": "window-close.png",
            "tab-close-active": "window-close-act.png",
            "resume": "resume48.png",
            "zoom": "zoom48.png",
            "quit": "quit48.png",
        }
    else:
        images = {
            "run-current-script": "media-playback-start.png",
            "stop": "process-stop.png",
            "new-file": "document-new.png",
            "open-file": "open_file.png",
            "save-file": "document-save.png",
            "debug-current-script": "debug-run.png",
            "step-over": "debug-step-over.png",
            "step-into": "debug-step-into.png",
            "step-out": "debug-step-out.png",
            "run-to-cursor": "debug-run-cursor.png",
            "tab-close": "window-close.png",
            "tab-close-active": "window-close-act.png",
            "resume": "resume.png",
            "zoom": "zoom.png",
            "quit": "quit.png",
        }

    #Change the types of input images depending on the image that is selected.
    res_dir = os.path.join(os.path.dirname(__file__), "res")
    theme_image_map = {}
    for image in images:
        theme_image_map[image] = os.path.join(res_dir, images[image])


    #Create a given theme. Similar to Rasberry Pi but with modified buttons
    get_workbench().add_ui_theme("JuiceMind-Theme", "Enhanced Clam", pix, theme_image_map)

    #Set our theme equal to the default theme during the launch of the IDE
    get_workbench().set_option("view.ui_theme", startup_theme)

    micropython_image = os.path.join(res_dir, "MCU.png")
    computer_selected_image = os.path.join(res_dir, "computer_selected.png")
    connect_image = os.path.join(res_dir, "connect.png")
    transparent_background = os.path.join(res_dir, "transparent_background.png")

    #Set the initial backend to be default, normal computer


    #Change the backend to ESP8266
    get_workbench().set_option("run.backend_name", "SameAsFrontend")



    '''
    #Add a button to switch to MicroPython Interpreter
    get_workbench().add_command("Switch MicroPython", "tools", "Run with MicroPython",
                                switch_to_microPython,
                                default_sequence=select_sequence("<Control-e>", "<Command-e>"),
                                group=120,
                                tester=disable_MCU,
                                image = micropython_image,
                                caption="Use MicroPython",
                                include_in_toolbar=True)
    '''


    '''
    #Add command on toolbar to implement regular Python Interpreter
    get_workbench().add_command("Switch Regular Python", "tools", "Run with Computer Python",
                                switch_to_python,
                                default_sequence=select_sequence("<Control-e>", "<Command-e>"),
                                group=120,
                                tester=disable_computer,
                                image = computer_image,
                                caption="Use Python",
                                include_in_toolbar=True)

    '''

    get_workbench().add_command("add_spacing", "tools", "",
                                toggle_python,
                                default_sequence=select_sequence("<Control-e>", "<Command-e>"),
                                group=120,
                                tester=always_disabled,
                                image = transparent_background,
                                caption="Use Python",
                                include_in_toolbar=True,
                                include_in_menu=False)

    #One command on the toolbar that toggles between Python image and microcontroller image
    get_workbench().add_command("toggle_python", "tools", "Toggle Python",
                                toggle_python,
                                default_sequence=select_sequence("<Control-e>", "<Command-e>"),
                                group=120,
                                tester=always_enabled,
                                image = computer_selected_image,
                                caption="Use Python",
                                include_in_toolbar=True)




    #Add command on toolbar to connect
    get_workbench().add_command("connect_button", "tools", "",
                                connect_device,
                                default_sequence=select_sequence("<Control-e>", "<Command-e>"),
                                group=120,
                                tester=test_connection,
                                image = connect_image,
                                caption="Connect Button",
                                include_in_toolbar=True)