from utilities import Utilities
import pandas as pd

utl = Utilities()

# read list european union
df_people_eu =  pd.read_csv('./unit_test/test_data/list_eu_people_02022021.csv', sep=';')
df_entities_eu = pd.read_csv('./unit_test/test_data/list_eu_entities_02022021.csv', sep=';')

# read list state secretary
df_entities_ss = pd.read_csv('./unit_test/test_data/list_ssus_entities_12012021.csv', sep=';')

# read list ofac-clinton
df_people_ofac = pd.read_csv('./unit_test/test_data/list_ofac_people_12012021.csv', sep=';')
df_entities_ofac = pd.read_csv('./unit_test/test_data/list_ofac_entities_12012021.csv', sep=';')

# read list onu
df_people_onu = pd.read_csv('./unit_test/test_data/list_onu_people_12012021.csv', sep=';')
df_entities_onu = pd.read_csv('./unit_test/test_data/list_onu_entities_12012021.csv', sep=';')

# read list ficticial vendors
df_thirdpart_fv = pd.read_csv('./unit_test/test_data/list_fv_data_12012021.csv', sep=';')


def Normalize(text):
    assert utl.normalize(text), 'Falla'
Normalize('aplicación')

def digit_input_validation():
    list_ = ["1234"]
    assert utl.digit_input_validation(list_), 'Falla'
digit_input_validation()
    
def alphanum_input_validation():
    list_ = ["carro"]
    assert utl.alphanum_input_validation(list_), 'Falla'
alphanum_input_validation()

def flat_column():
    list_ = ['[]', '[]', '[]', "['07442833']", '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]', '[]']
    assert utl.flat_column(list_), 'Falla'
flat_column()

def list_validation():
    names = ['hamed abdollahi', 'abdelkarim hussein mohamed al nasser', 'ibrahim salih mohammed al yacoub', 'manssor arbabsiar', 'assadollah asadi', 'mohamed bouyeri', 'hassan hassan el hajj', 'saeid hashemi moghadam', 'hasan izz al din', 'farah meliad', 'khalid shaikh mohammed', 'dalokay șanli', 'abdul reza shahlai', 'ali gholam shakuri', 'qasem soleimani', 'organizacion abu nidal', 'oan', 'consejo revolucionario de al fatah', 'brigadas revolucionarias arabes', 'septiembre negro', 'organizacion revolucionaria de los musulmanes socialistas', 'brigada de los martires de al aqsa', 'al aqsa ev', 'babbar jalsa', 'partido comunista de las filipinas', 'nuevo ejercito del pueblo', 'nep', "new people's army", 'npa', 'ireccion de la seguridad interior del ministerio de inteligencia y seguridad irani', 'al gama al islamiya', "al gama'a al islamiyya", 'grupo islamico', 'gi', 'i̇slami buyuk doğu akıncılar cephesi', 'ibda c']
    list_ = ['santiago arboleda', 'sebastian cardenas', 'antonio perez']
    assert utl.list_validation(names, list_), 'Falla'
list_validation()

def result_by_name():
    list_ = ['santiaago arboleda', 'hamed abdollahi', 'sebastian cardenas']
    df_people_pep = pd.DataFrame(list_)
    count = [1,1,10]
    df_people_pep["cantidad"] = count
    df_people_pep["cantidad"] = df_people_pep["cantidad"].astype(int)
    df = utl.result_by_name(list_, df_people_eu, df_entities_eu, df_entities_ss, df_people_ofac, df_entities_ofac, df_people_onu, df_entities_onu, df_thirdpart_fv, df_people_pep)
    print(df)
    assert len(df.columns) > 1, 'Falla'
result_by_name()

def result_by_id():
    list_ = ['1036621336', '1017179741', '17845415']
    df = utl.result_by_id(list_, df_people_eu, df_people_onu, df_thirdpart_fv)
    print(df)
    assert len(df.columns) > 1, 'Falla'
result_by_id()

def result_by_passport():
    list_ = ['an945621', 'bg584136', 'hagb320']
    df = utl.result_by_passport(list_, df_people_eu, df_people_onu)
    print(df)
    assert len(df.columns) > 1, 'Falla'
result_by_passport()





