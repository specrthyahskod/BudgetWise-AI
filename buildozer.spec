[app]

# (str) Title of your application
title = BudgetWise AI

# (str) Package name
package.name = budgetwiseai

# (str) Package domain
package.domain = org.budgetwise

# (str) Source code where main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,svg,txt

# (str) Application version number
version = 0.1

# (list) Application requirements
requirements = python3,kivy,requests

# (str) Application icon filename
icon.filename = %(source.dir)s/assets/BudgetWise_AI_logo.png

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen or not
fullscreen = 0

# (list) Permissions
permissions = INTERNET

# (bool) Automatically accept SDK licenses in CI environments
android.accept_sdk_license = True

# (str) Target Architecture (Set to single target for reliable CI compilation)
android.archs = arm64-v8a

# (str) Android NDK version
android.ndk = 25b

# (int) Target Android API
android.api = 33

# (int) Minimum API supported
android.minapi = 21

[buildozer]

# (int) Log level
log_level = 2

# (int) Display warning if run as root
warn_on_root = 1