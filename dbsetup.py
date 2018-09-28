import datetime

from dbhelper import DBHelper

#to setup database and create master admin account

user = "admin" #username for masteradmin
passwd = "1234" #4 digit pin for masteradmin
depts = ["dept1", "dept2", "dept3"] #list of dept names in ""
date = "01/01/2018" #history up to before date to clear in dd/mm/yyyy


def main():
    db = DBHelper()
    db.setup(user, passwd) ##<<run to setup for 1st time
    db.setupdepts(depts)    ##<<run to modify/add dept 
    #db.clearhistory(date)  ##<<run to clearhistory
    db.close()


if __name__ == '__main__':
    main()