from distutils.core import setup
import py2exe

setup(
    windows=[{
        "script": 'UI.py',
        "icon_resources": [{1, "link_icon.ico"}]
    }]
    )
