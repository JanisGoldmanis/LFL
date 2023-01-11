from neo4j import GraphDatabase
import LoadData
import GetData

run = True


def execute_transactions(transaction_exection_commands):
    data_base_connection = GraphDatabase.driver(uri="bolt://localhost:7687", auth=("neo4j", "password"))
    session = data_base_connection.session()
    for i in transaction_exection_commands:
        session.run(i)


while run:
    print('')
    print('Pick one:')
    print('1: Load Protocol')
    print('2: Load interval')
    print('3: Delete everything')
    print('4: Get data from database')
    print('x: Exit application')

    case = input('Input: ')

    if case == 'x':
        run = False

    elif case == '3':
        transaction_execution_commands = ["MATCH (n) DETACH DELETE n"]
        execute_transactions(transaction_execution_commands)
        print('Done - all data deleted')

    elif case == '1':
        protocol_nr = int(input('Protocol: '))
        if protocol_nr in [1, 2, 3, 4, 5, 6]:
            print(f'Loading procotol {protocol_nr}')
            transaction_execution_commands = LoadData.load_data(f'futbols{protocol_nr}.json')
            execute_transactions(transaction_execution_commands)
            print('Protocol added to database')
        else:
            print('invalid number')

    elif case == '2':
        protocol_str = input('Protocol interval (x-y): ')
        if len(protocol_str) != 3 or protocol_str[1] != '-' or not protocol_str[0].isnumeric() or not protocol_str[
            2].isnumeric():
            print('Invalid input, please input in format "x-y"')
        elif protocol_str[0] > protocol_str[2]:
            print('Invalid range, please input x<y')
        else:
            nr1 = int(protocol_str[0])
            nr2 = int(protocol_str[2])
            print(f'Parsing from {nr1} to {nr2}')
            for num in range(nr1, nr2 + 1):
                print(f'Parsing protocol futbols{num}.json')
                transaction_execution_commands = LoadData.load_data(f'futbols{num}.json')
                execute_transactions(transaction_execution_commands)
                print('Protocol added to database')
            print('All protocols added to database!')

    elif case == '4':
        GetData.get_data()


