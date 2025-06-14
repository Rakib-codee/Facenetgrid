import os
from db_manager import DBManager

def test_log_and_get_history():
    db_path = 'test_history.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    db = DBManager(db_path=db_path)
    db.log_match('User1', 'Matched')
    db.log_match('User2', 'Added')
    history = db.get_history(limit=10)
    assert len(history) >= 2
    assert history[0][0] == 'User2' or history[1][0] == 'User2'
    os.remove(db_path)

def test_export_history_csv():
    db_path = 'test_history.db'
    if os.path.exists(db_path):
        os.remove(db_path)
    db = DBManager(db_path=db_path)
    db.log_match('User3', 'Matched')
    csv_str = db.export_history_csv()
    assert 'User3' in csv_str
    os.remove(db_path)

if __name__ == '__main__':
    test_log_and_get_history()
    test_export_history_csv()
    print('All DBManager tests passed!') 