[app]

# (str) Title of your application
title = BudgetWise AI

# (str) Package name
package.name = budgetwiseai

# (str) Package domain (needed for android/ios packaging)
package.domain = org.budgetwise

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (file extensions)
source.include_exts = py,png,jpg,kv,atlas,json,svg

# (list) Application requirements
requirements = python3,kivy,requests,pyqt5

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
permissions = INTERNET

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = false, 1 = true)
warn_on_root = 1