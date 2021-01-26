from list_eu.utilities import Utilities
import re 
import string

utl_eu = Utilities()

def normalize(s):
    assert utl_eu.normalize(s), 'Falla'
normalize('aplicación')
    
def remove_punctuation(text):
    assert utl_eu.remove_punctuation(text), 'Falla'
remove_punctuation('Con esto termina la frase.')

#def fill_entities_data(text):
 #   assert utl_eu.fill_entities_data(text), 'Falla'
#list_ = ['1.«Organización Abu Nidal» — («OAN») (otras denominaciones: «Consejo Revolucionario de Al Fatah», «Brigadas Revolucionarias Árabes», «Septiembre Negro» y «Organización Revolucionaria de los Musulmanes Socialistas»).', '2.«Brigada de los Mártires de Al-Aqsa».', '3.«Al-Aqsa e.V.».', '4.«Babbar Jalsa».', "5.«Partido Comunista de las Filipinas», incluido el «Nuevo Ejército del Pueblo» — «NEP» («New People's Army» — «NPA»), Filipinas.", '6.Dirección de la Seguridad Interior del Ministerio de Inteligencia y Seguridad iraní.', "7.«Al Gama al Islamiya» (otras denominaciones: «Al-Gama'a al-Islamiyya») («Grupo Islámico» — «GI»).", '8.«İslami Büyük Doğu Akıncılar Cephesi» — «IBDA-C» («Frente de Guerreros del Gran Oriente Islámico»).', '9.«Hamás», incluido «Hamas-Izz al-Din al-Qassem».', "10.«Ala militar de Hizbulá» [otras denominaciones: «Ala militar de Hezbolá», «Ala militar de Hizbulah», «Ala militar de Hizbolah», «Ala militar de Hezbalah», «Ala militar de Hisbolah», «Ala militar de Hizbu'llah», «Ala militar de Hizb Allah», «Consejo de la Yihad» (y todas las unidades bajo su mando, incluida la Organización de Seguridad Exterior)].", '11.«Hizbul Muyahidín» — «HM».']
#fill_entities_data(list_)

def get_data():
    assert utl_eu.get_data_eu_list(), 'Falla'
get_data()