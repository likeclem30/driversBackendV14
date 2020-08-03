from drivers_backend.app import create_app
from drivers_backend.models import DriverModel
from datetime import datetime

if __name__ == '__main__':
    application = create_app()
    application.app_context().push()

    # Create some test data
    test_data = [
        # username, timestamp, text
        ('bruce', datetime.now(), "k1G", "Karut", "0", "45", "+2349020193487",
         "A2J", "K4G", "Karu4", "A2J", "Karu4r", "A2J", "K4G", "1",
         datetime.now(), "Nathan", "Doe", '67', 'brown', 'a link'),
        ('mike', datetime.now(), "K2G", "Karu2t", "1", "20", "+2349020193487",
         "A2J", "K4G", "Karu4", "A2J", "Karu4", "A2J", "K4G", "1",
         datetime.now(), "Tony", "Stark", '56', 'chris', 'a link'),
        ('bruce', datetime.now(), "K3G", "Karu3t", "2", "3", "+2349020193487",
         "A2J", "K4G", "Karu4", "A2J", "Karu4", "A2J", "K4G", "0",
         datetime.now(), "John", "Jack", '78', 'stark', 'a link'),
        ('jack', datetime.now(), "K4G", "Karu4t", "0", "43", "+2349020193487",
         "A2J", "K4G", "Karu4", "A2J", "Karu4", "A2J", "K4G", "0",
         datetime.now(), "Mike", "Alex", '109', 'drake', 'a link')

    ]
    for username, timestamp, residentialaddress, email, status, pin,\
            phoneno, bankname, accountname, accountnumber, zone,\
            area, route, geofencedarea, appstatus, approvedtimestamp,\
            firstname, lastname, operatorid, usernamemain, license\
            in test_data:
        driver = DriverModel(
            username=username, residentialaddress=residentialaddress,
            email=email, status=status, timestamp=timestamp, pin=pin,
            bankname=bankname, accountname=accountname, route=route,
            accountnumber=accountnumber, zone=zone, area=area,
            appstatus=appstatus, geofencedarea=geofencedarea,
            approvedtimestamp=approvedtimestamp, phoneno=phoneno,
            firstname=firstname, lastname=lastname, operatorid=operatorid,
            usernamemain=usernamemain, license=license
            )
        application.db.session.add(driver)

    application.db.session.commit()
