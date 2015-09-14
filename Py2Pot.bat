REM @echo off
goto comment
This file signals the pygettext python module to get all the strings for translation and the docstrings.

Author	Adrian Hornung
Date	14.09.2015
:comment
SET Modules=src/*.py src/language/*.py src/messages/*.py src/parsers/*.py src/sql/*.py

py -3.4  C:\PYthon34\Tools\i18n\pygettext.py -n --keyword=_ --default-domain=Telegram --output-dir=translation %Modules%

pause