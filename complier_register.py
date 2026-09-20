import os
import sys
import winreg

def register():
    # Use pythonw so no black command prompt opens behind the window
    python_exe = sys.executable
    pythonw_exe = os.path.join(os.path.dirname(python_exe), "pythonw.exe")
    runner = pythonw_exe if os.path.exists(pythonw_exe) else python_exe

    # Find the full path to rcd_viewer.py
    project_root = os.path.dirname(os.path.abspath(__file__))
    viewer_script = os.path.join(project_root, "rcd_viewer.py")
    if not os.path.exists(viewer_script):
        viewer_script = os.path.join(project_root, "tools", "rcd_viewer.py")

    # The exact command Windows runs when double-clicking
    command = f'"{runner}" "{viewer_script}" "%1"'
    prog_id = "BudgetWise.RCDViewer.1"

    try:
        # Register the app command
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"Software\Classes\{prog_id}\shell\open\command") as k:
            winreg.SetValue(k, "", winreg.REG_SZ, command)

        # Link .rcd to this app
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Classes\.rcd") as k:
            winreg.SetValue(k, "", winreg.REG_SZ, prog_id)

        print("Registered association successfully!")
        print(f"Command set to: {command}")
    except Exception as e:
        print(f"Failed to register: {e}")

if __name__ == "__main__":
    register()