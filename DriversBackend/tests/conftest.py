import pytest
import http.client
from drivers_backend.app import create_app
from .constants import PRIVATE_KEY
from drivers_backend import token_validation
from faker import Faker
fake = Faker()


@pytest.fixture
def app():
    application = create_app()

    application.app_context().push()
    # Initialise the DB
    application.db.create_all()

    return application


@pytest.fixture
def driver_fixture(client):
    '''
    Generate three drivers in the system.
    '''

    driver_ids = []
    for _ in range(3):
        driver = {
            'firstname': fake.text(240),
            'lastname': fake.text(240),
            'residentialaddress': fake.text(240),
            'email': fake.text(240),
            'phoneno': fake.text(240),
            'status': fake.text(240),
            'pin': fake.text(240),
            'operatorid': fake.text(240),
            'reviews': fake.text(240),
            'bankname': fake.text(240),
            'accountname': fake.text(240),
            'accountnumber': fake.text(240),
            'license': fake.text(240),
            'zone': fake.text(240),
            'area': fake.text(240),
            'route': fake.text(240),
            'geofencedarea': fake.text(240),
            'appstatus': fake.text(240),
            'usernamemain': fake.text(240),
        }
        header = token_validation.generate_token_header(fake.name(),
                                                        PRIVATE_KEY)
        headers = {
            'Authorization': header,
        }
        response = client.post('/api/me/drivers/', data=driver,
                               headers=headers)
        assert http.client.CREATED == response.status_code
        result = response.json
        driver_ids.append(result['id'])

    yield driver_ids

    # Clean up all drivers
    response = client.get('/api/drivers/')
    drivers = response.json
    for driver in drivers:
        driver_id = driver['id']
        url = f'/admin/drivers/{driver_id}/'
        response = client.delete(url)
        assert http.client.NO_CONTENT == response.status_code
