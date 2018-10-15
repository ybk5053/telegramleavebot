from dbhelper import DBHelper

def main():
    db = DBHelper()
    super_id = db.findsuper('Drafting')
    for users in super_id:
        print(users[0])
    db.close()


if __name__ == '__main__':
    main()