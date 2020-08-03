'''
Test the Drivers operations


Use the driver_fixture to have data to retrieve, it generates three drivers
'''
from unittest.mock import ANY
import http.client
from freezegun import freeze_time
from .constants import PRIVATE_KEY
from drivers_backend import token_validation
from faker import Faker
fake = Faker()


@freeze_time('2019-05-07 13:47:34')
def test_create_me_driver(client):
    new_driver = {
        'username': fake.name(),
        'firstname': fake.text(240),
        'lastname': fake.text(240),
        'residentialaddress': fake.text(240),
        'email': fake.text(240),
        'phoneno': fake.text(240),
        'status': fake.text(240),
        'pin': fake.text(240),
        'operatorid': fake.text(240),
        'bankname': fake.text(240),
        'accountname': fake.text(240),
        'accountnumber': fake.text(240),
        'license': fake.text(240),
        'zone': fake.text(240),
        'area': fake.text(240),
        'route': fake.text(240),
        'geofencedarea': fake.text(240),
        'usernamemain': fake.text(240),
        'appstatus': fake.text(240),
    }
    header = token_validation.generate_token_header(fake.name(),
                                                    PRIVATE_KEY)
    headers = {
        'Authorization': header,
    }
    response = client.post('/api/me/drivers/', data=new_driver,
                           headers=headers)
    result = response.json

    assert http.client.CREATED == response.status_code

    expected = {
        'id': ANY,
        'username': ANY,
        'firstname': new_driver['firstname'],
        'lastname': new_driver['lastname'],
        'residentialaddress': new_driver['residentialaddress'],
        'email': new_driver['email'],
        'phoneno': new_driver['phoneno'],
        'status': new_driver['status'],
        'pin': new_driver['pin'],
        'operatorid': new_driver['operatorid'],
        'bankname': new_driver['bankname'],
        'accountname': new_driver['accountname'],
        'accountnumber': new_driver['accountnumber'],
        'license': new_driver['license'],
        'approvedtimestamp': ANY,
        'zone': new_driver['zone'],
        'area': new_driver['area'],
        'route': new_driver['route'],
        'geofencedarea': new_driver['geofencedarea'],
        'appstatus': new_driver['appstatus'],
        'acceptstatus': ANY,
        'accepttimestamp': ANY,
        'usernamemain': new_driver['usernamemain'],
        'timestamp': '2019-05-07T13:47:34',
    }
    assert result == expected


def test_create_me_unauthorized(client):
    new_driver = {
        'username': fake.name(),
        'firstname': fake.text(240),
        'lastname': fake.text(240),
        'residentialaddress': fake.text(240),
        'email': fake.text(240),
        'phoneno': fake.text(240),
        'status': fake.text(240),
        'pin': fake.text(240),
        'operatorid': fake.text(240),
        'bankname': fake.text(240),
        'accountname': fake.text(240),
        'accountnumber': fake.text(240),
        'license': fake.text(240),
        'zone': fake.text(240),
        'area': fake.text(240),
        'route': fake.text(240),
        'geofencedarea': fake.text(240),
        'usernamemain': fake.text(240),
        'appstatus': fake.text(240),
    }
    response = client.post('/api/me/drivers/', data=new_driver)
    assert http.client.UNAUTHORIZED == response.status_code


def test_list_me_drivers(client, driver_fixture):
    username = fake.name()
    firstname = fake.text(240)
    lastname = fake.text(240)
    residentialaddress = fake.text(240)
    email = fake.text(240)
    phoneno = fake.text(240)
    status = fake.text(240)
    pin = fake.text(240)
    operatorid = fake.text(240)
    bankname = fake.text(240)
    accountname = fake.text(240)
    accountnumber = fake.text(240)
    license = fake.text(240)
    zone = fake.text(240)
    area = fake.text(240)
    route = fake.text(240)
    usernamemain = fake.text(240)
    geofencedarea = fake.text(240)
    appstatus = fake.text(240)

    # Create a new driver
    new_driver = {
        'firstname': firstname,
        'lastname': lastname,
        'residentialaddress': residentialaddress,
        'email': email,
        'phoneno': phoneno,
        'status': status,
        'pin': pin,
        'operatorid': operatorid,
        'bankname': bankname,
        'accountname': accountname,
        'accountnumber': accountnumber,
        'license': license,
        'zone': zone,
        'area': area,
        'route': route,
        'geofencedarea': geofencedarea,
        'usernamemain': usernamemain,
        'appstatus': appstatus,
    }
    header = token_validation.generate_token_header(username,
                                                    PRIVATE_KEY)
    headers = {
        'Authorization': header,
    }
    response = client.post('/api/me/drivers/', data=new_driver,
                           headers=headers)
    result = response.json

    assert http.client.CREATED == response.status_code

    # Get the drivers of the user
    response = client.get('/api/me/drivers/', headers=headers)
    results = response.json

    assert http.client.OK == response.status_code
    assert len(results) == 1
    result = results[0]
    expected_result = {
        'id': ANY,
        'username': username,
        'firstname': firstname,
        'lastname': lastname,
        'residentialaddress': residentialaddress,
        'email': email,
        'phoneno': phoneno,
        'status': status,
        'pin': pin,
        'operatorid': operatorid,
        'bankname': bankname,
        'accountname': accountname,
        'accountnumber': accountnumber,
        'license': license,
        'zone': zone,
        'area': area,
        'route': route,
        'geofencedarea': geofencedarea,
        'appstatus': appstatus,
        'usernamemain': usernamemain,
        'approvedtimestamp': ANY,
        'timestamp': ANY,
        'acceptstatus': ANY,
        'accepttimestamp': ANY,
    }
    assert result == expected_result


def test_list_me_unauthorized(client):
    response = client.get('/api/me/drivers/')
    assert http.client.UNAUTHORIZED == response.status_code


def test_list_drivers(client, driver_fixture):
    response = client.get('/api/drivers/')
    result = response.json

    assert http.client.OK == response.status_code
    assert len(result) > 0

    # Check that the ids are increasing
    previous_id = -1
    for driver in result:
        expected = {
            'firstname': ANY,
            'lastname': ANY,
            'residentialaddress': ANY,
            'email': ANY,
            'phoneno': ANY,
            'status': ANY,
            'pin': ANY,
            'operatorid': ANY,
            'bankname': ANY,
            'accountname': ANY,
            'accountnumber': ANY,
            'license': ANY,
            'zone': ANY,
            'area': ANY,
            'route': ANY,
            'geofencedarea': ANY,
            'appstatus': ANY,
            'approvedtimestamp': ANY,
            'acceptstatus': ANY,
            'accepttimestamp': ANY,
            'usernamemain': ANY,
            'username': ANY,
            'id': ANY,
            'timestamp': ANY,
        }
        assert expected == driver
        assert driver['id'] > previous_id
        previous_id = driver['id']


def test_list_drivers_search(client, driver_fixture):
    username = fake.name()
    firstname = fake.text(240)
    lastname = fake.text(240)
    residentialaddress = fake.text(240)
    email = fake.text(240)
    phoneno = fake.text(240)
    status = fake.text(240)
    pin = fake.text(240)
    operatorid = fake.text(240)
    bankname = fake.text(240)
    accountname = fake.text(240)
    accountnumber = fake.text(240)
    license = fake.text(240)
    zone = fake.text(240)
    area = fake.text(240)
    usernamemain = fake.text(240)
    route = 'platypus'
    geofencedarea = fake.text(240)
    appstatus = fake.text(240)
    new_driver = {
        'firstname': firstname,
        'lastname': lastname,
        'residentialaddress': residentialaddress,
        'email': email,
        'phoneno': phoneno,
        'status': status,
        'pin': pin,
        'operatorid': operatorid,
        'bankname': bankname,
        'accountname': accountname,
        'accountnumber': accountnumber,
        'license': license,
        'zone': zone,
        'area': area,
        'route': route,
        'geofencedarea': geofencedarea,
        'usernamemain': usernamemain,
        'appstatus': appstatus,
    }
    header = token_validation.generate_token_header(username,
                                                    PRIVATE_KEY)
    headers = {
        'Authorization': header,
    }
    response = client.post('/api/me/drivers/', data=new_driver,
                           headers=headers)
    assert http.client.CREATED == response.status_code

    response = client.get('/api/drivers/?search=platypus')
    result = response.json

    assert http.client.OK == response.status_code
    assert len(result) > 0

    # Check that the returned values contain "platypus"
    for driver in result:
        expected = {
            'firstname': ANY,
            'lastname': ANY,
            'residentialaddress': ANY,
            'email': ANY,
            'phoneno': ANY,
            'status': ANY,
            'pin': ANY,
            'operatorid': ANY,
            'bankname': ANY,
            'accountname': ANY,
            'accountnumber': ANY,
            'license': ANY,
            'zone': ANY,
            'area': ANY,
            'route': ANY,
            'geofencedarea': ANY,
            'appstatus': ANY,
            'approvedtimestamp': ANY,
            'acceptstatus': ANY,
            'accepttimestamp': ANY,
            'usernamemain': ANY,
            'username': username,
            'id': ANY,
            'timestamp': ANY,
        }
        assert expected == driver
        assert 'platypus' in driver['route'].lower()


def test_get_driver(client, driver_fixture):
    driver_id = driver_fixture[0]
    response = client.get(f'/api/drivers/{driver_id}/')
    result = response.json

    assert http.client.OK == response.status_code
    assert 'firstname' in result
    assert 'lastname' in result
    assert 'residentialaddress' in result
    assert 'email' in result
    assert 'phoneno' in result
    assert 'status' in result
    assert 'pin' in result
    assert 'operatorid' in result
    assert 'bankname' in result
    assert 'accountname' in result
    assert 'accountnumber' in result
    assert 'approvedtimestamp' in result
    assert 'accepttimestamp' in result
    assert 'license' in result
    assert 'usernamemain' in result
    assert 'zone' in result
    assert 'area' in result
    assert 'route' in result
    assert 'geofencedarea' in result
    assert 'appstatus' in result
    assert 'acceptstatus' in result
    assert 'username' in result
    assert 'timestamp' in result
    assert 'id' in result


def test_get_non_existing_driver(client, driver_fixture):
    driver_id = 123456
    response = client.get(f'/api/drivers/{driver_id}/')

    assert http.client.NOT_FOUND == response.status_code
