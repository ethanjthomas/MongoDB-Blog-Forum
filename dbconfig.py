from configparser import ConfigParser

def read_db_config(filename='Team27Lab4.ini', section='mongodb'):
    parser = ConfigParser()
    parser.read(filename)

    dbconfig = {}
    if parser.has_section(section):
        items = parser.items(section)

        for item in items:
            dbconfig[item[0]] = item[1]

    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    uri = 'mongodb+srv://{}:{}@cluster0.uzrhjr1.mongodb.net/?retryWrites=true&w=majority'.format(dbconfig['user'], dbconfig['pass']).replace("\'",'')

    return uri