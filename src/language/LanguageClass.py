#!/usr/bin/python
# -*- coding: utf-8 -*-

import gettext
 
def CreateTranslationObject( 
                            Languages = ["de", "en"], 
                            Localedir='language',
                            ):
    """
    This function returns a gettext object.
    
    Variables:
        Languages            array of string
            contains the language string
        Localedir            string
            contains the Language location 
    """
    if type(Languages) == type('str'):
        Languages = [Languages]
    
    LanguageObject = gettext.translation("Telegram", 
                               localedir=Localedir,
                               languages=Languages
                               )

    return LanguageObject

if __name__ == "__main__":
    i = CreateTranslationObject(localedir="../language")

