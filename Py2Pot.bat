rem @echo off

goto comment
This file signals the pygettext python module to get all the strings for translation and the docstrings.

Author	Adrian Hornung
Date	14.09.2015
:comment

cd src

SET Modules=*.py language/*.py messages/*.py parsers/*.py sql/*.py

echo getting the strings
py -3.4  C:\PYthon34\Tools\i18n\pygettext.py -n --keyword=_ --keyword=M_ --default-domain=Telegram --output-dir=../translation %Modules%
echo done getting the strings
cd ..

pause