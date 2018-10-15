from dbhelper import DBHelper

def main():
    db = DBHelper()
    db.resetleave()     ##<<run to add leave for new year
    db.close()


if __name__ == '__main__':
    main()