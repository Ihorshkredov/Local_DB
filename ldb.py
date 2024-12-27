import pandas as pd
import datetime
import sqlite3
import matplotlib.pyplot as plt
import time

#_____FUNCTIONS______
def connect_to_db(db_file_address):
    """Connects to sqlite db file.
    Returns Tuple -> (Pandas data frames, str(indicator of conection))"""
    indicator = 'NO DATA'
    data_full_test = 'NO DATA'
    data_steps = 'NO DATA'
    with(sqlite3.connect(db_file_address)) as connection:
        try:
            command_full_test = 'SELECT * FROM FullTest'
            command_steps = 'SELECT * FROM SimpleTest'
            data_full_test = pd.read_sql(command_full_test, connection)
            data_steps = pd.read_sql(command_steps, connection)
        except Exception as ex:
            indicator = 'ERROR'
        else:
            indicator = 'OK'
    
    return (data_full_test, data_steps, indicator)

def get_data_for_sn(data_frame, serial_number):
    return data_frame[data_frame['SN'] == serial_number]

def get_data_for_period(data_frame, date_from, date_to):
    mask = (data_frame['DateTime'] >= date_from) & (data_frame['DateTime'] <= date_to)
    return data_frame[mask]
    
def get_general_statistic(data_frame):
    tested = len(data_frame)
    passed = len(data_frame[ data_frame['Status'] == 'Passed'])
    failed = len(data_frame[data_frame['Status'] == 'Failed'])
    aborted = len(data_frame[data_frame['Status'] == 'Aborted'])
    return (tested, passed, failed, aborted)

def get_test_details(steps_data_frame, serial_number, date_time):
    mask = (steps_data_frame['SN'] == str(serial_number)) & (steps_data_frame['DateTime'] == str(date_time))
    return steps_data_frame[mask]
   
def generate_tests_statistic(filtered_steps_df):
    result = {'Name':[], 'Passed':[], 'Failed':[], 'Aborted':[]}
    for test in filtered_steps_df.SimpleTestName.unique():
        result['Name'].append(test)
        statuses = filtered_steps_df.loc[filtered_steps_df['SimpleTestName'] == test]
        result['Passed'].append(len(statuses[statuses['SimpleTestStatus'] == 'Passed']))
        result['Failed'].append(len(statuses[statuses['SimpleTestStatus'] == 'Failed']))
        result['Aborted'].append(len(statuses[statuses['SimpleTestStatus'] == 'Aborted']))
  
    return pd.DataFrame(result)

def show_graph(step_name, test_steps_filtered_df):
    
    filtered_data = test_steps_filtered_df[test_steps_filtered_df['SimpleTestName']== step_name]

    y_values = [float(x) for x in filtered_data['SimpleTestValue'].tolist()]
    low_limit = [float(t) for t in filtered_data['SimpleTestLL'].tolist()]

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=False)
    ax1.set_title(step_name)
    ax1.plot( range(len(y_values)), y_values, marker = 'o')
    ax1.plot(low_limit, color = 'r')

    if check_if_float(filtered_data['SimpleTestHL'].tolist()[0]):
        
        high_limit = [float(x) for x in filtered_data['SimpleTestHL'].tolist()]
        ax1.plot(range(len(high_limit)),high_limit, color='r')

    ax2.set_title('Normal Distribution')
    ax2.hist(y_values)
    ax2.axvline( x = low_limit[0], color = 'r', linestyle = '-')
    if check_if_float(filtered_data['SimpleTestHL'].tolist()[0]):
        H_limit = float(filtered_data['SimpleTestHL'].tolist()[0])
        ax2.axvline( x = H_limit, color = 'r', linestyle = '-')

    fig.tight_layout()
    fig.show()

def show_all_status_for_step(step_name, test_steps_filtered_df):
    filtered_data = test_steps_filtered_df[test_steps_filtered_df['SimpleTestName']== step_name]
    ordered_data = filtered_data.reset_index(drop=True)
    ordered_data['index'] = ordered_data.index
    return ordered_data[['index','DateTime','SN', 'SimpleTestStatus','SimpleTestValue']]

def check_if_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    

#_____SELF TEST_____
if __name__ == '__main__':
    
    global steps

    full_test, steps, indicator = connect_to_db('Tester_v2.db')
    data_for_sn = get_data_for_sn(steps,'E2185D224031363100456' )

    data_details = get_test_details(steps, '302059207','2024-04-23T04:30:09.670' )


    data_for_period = get_data_for_period(steps,'2024-04-18T09:00:00','2024-04-18T12:00:00')

    details_data = show_all_status_for_step('WATS PN', steps)

    

    for i, row in details_data.iterrows():
        print( i, row)
   

    results = data_for_period[data_for_period['SimpleTestName'] == 'WATS PN'].count()
    print('SELF TEST DONE')
