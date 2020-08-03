import http.client
import requests
from threading import Thread
from datetime import datetime, timedelta
from flask_restplus import Namespace, Resource, fields
from drivers_backend import config
from drivers_backend.models import DriverModel
from drivers_backend.token_validation import validate_token_header
from drivers_backend.db import db
from flask import abort
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

DRIVER_MSG_URL = "http://165.22.116.11:7058/api/messages/driverwelcome/"
WELCOME_MSG_URL = "http://165.22.116.11:7058/api/messages/welcome/"

api_namespace = Namespace('api', description='API operations')


def authentication_header_parser(value):
    username = validate_token_header(value, config.PUBLIC_KEY)
    if username is None:
        abort(401)
    return username


def request(url, data):
    requests.post(url=url, data=data)
    print('Thread Exited')


def make_request(url, data):
    th = Thread(target=request,
                args=(url, data))
    return th


# Input and output formats for driver
authentication_parser = api_namespace.parser()
authentication_parser.add_argument('Authorization', location='headers',
                                   type=str,
                                   help='Bearer Access Token')

driver_parser = authentication_parser.copy()
driver_parser.add_argument('firstname', type=str, required=True,
                           help='Driver First Name')
driver_parser.add_argument('lastname', type=str, required=True,
                           help='Driver Last Name')
driver_parser.add_argument('lastname', type=str, required=True,
                           help='Driver Last Name')
driver_parser.add_argument('usernamemain', type=str, required=False,
                           help='Driver username')
driver_parser.add_argument('residentialaddress', type=str, required=True,
                           help='Drivers Address')
driver_parser.add_argument('email', type=str, required=True,
                           help='Driver email Address')
driver_parser.add_argument('phoneno', type=str, required=True,
                           help='Driver Phone No')
driver_parser.add_argument('status', type=str, required=False,
                           help='Has driver been approved')
driver_parser.add_argument('pin', type=str, required=True,
                           help='The Driver Zeno Pin')
driver_parser.add_argument('operatorid', type=str, required=False,
                           help='The Driver Operator id')
driver_parser.add_argument('bankname', type=str, required=True,
                           help='Drivers bank name')
driver_parser.add_argument('accountname', type=str, required=True,
                           help='Drivers bank account name')
driver_parser.add_argument('accountnumber', type=str, required=True,
                           help='Drivers bank account number')
driver_parser.add_argument('license', type=str, required=False,
                           help='The driver license link')
driver_parser.add_argument('zone', type=str, required=False,
                           help='Zone in which driver operates')
driver_parser.add_argument('area', type=str, required=False,
                           help='Area in which driver operates')
driver_parser.add_argument('route', type=str, required=False,
                           help='Route in which driver operates')
driver_parser.add_argument('geofencedarea', type=str, required=False,
                           help='Driver geo-fenced area')
driver_parser.add_argument('appstatus', type=str, required=False,
                           help='The driver online status')

model = {
    'id': fields.Integer(),
    'username': fields.String(),
    'firstname': fields.String(),
    'lastname': fields.String(),
    'usernamemain': fields.String(),
    'residentialaddress': fields.String(),
    'email': fields.String(),
    'phoneno': fields.String(),
    'status': fields.String(),
    'pin': fields.String(),
    'operatorid': fields.String(),
    'bankname': fields.String(),
    'accountname': fields.String(),
    'accountnumber': fields.String(),
    'license': fields.String(),
    'zone': fields.String(),
    'area': fields.String(),
    'route': fields.String(),
    'geofencedarea': fields.String(),
    'appstatus': fields.String(),
    'acceptstatus': fields.String(),
    'approvedtimestamp': fields.DateTime(),
    'accepttimestamp': fields.DateTime(),
    'timestamp': fields.DateTime(),
}
driver_model = api_namespace.model('Driver', model)


@api_namespace.route('/me/drivers/')
class MeDriverListCreate(Resource):

    @api_namespace.doc('list_drivers')
    @api_namespace.expect(authentication_parser)
    @api_namespace.marshal_with(driver_model, as_list=True)
    def get(self):
        '''
        retrives the details of driver(s) added by a particlar admin
        '''
        args = authentication_parser.parse_args()
        username = authentication_header_parser(args['Authorization'])

        drivers = (
            DriverModel
            .query
            .filter(DriverModel.username == username)
            .order_by('id')
            .all()
            )
        return drivers

    @api_namespace.doc('create_driver')
    @api_namespace.expect(driver_parser)
    def post(self):
        '''
        Create a new driver
        '''
        args = driver_parser.parse_args()
        username = authentication_header_parser(args['Authorization'])
        route = args['route']
        phoneno = args['phoneno']
        usernamemain = args['usernamemain']
        # firstname = args['firstname']
        new_driver = DriverModel(
            username=username,
            firstname=args['firstname'],
            lastname=args['lastname'],
            usernamemain=usernamemain,
            residentialaddress=args['residentialaddress'],
            email=args['email'],
            phoneno=phoneno,
            status=args['status'],
            pin=args['pin'],
            operatorid=args['operatorid'],
            bankname=args['bankname'],
            accountname=args['accountname'],
            accountnumber=args['accountnumber'],
            license=args['license'],
            zone=args['zone'],
            area=args['area'],
            route=route,
            geofencedarea=args['geofencedarea'],
            appstatus=args['appstatus'],
            timestamp=datetime.utcnow())

        db.session.add(new_driver)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            result = {'result': 'Email already exists, try another one'}
            return result, http.client.UNPROCESSABLE_ENTITY

        # Send welcome Mail and message to Driver

        data = {
            'username': usernamemain,
            'recieverNo': phoneno,
            'recieverEmail': args['email'],
            'firstName': args['firstname'],
            'userPin': args['pin']
        }

        request = make_request(WELCOME_MSG_URL, data)
        request.start()

        result = api_namespace.marshal(new_driver, driver_model)

        return result, http.client.CREATED


search_parser = api_namespace.parser()
search_parser.add_argument('search', type=str, required=False,
                           help='Search in the text of the drivers')


@api_namespace.route('/drivers/')
class DriverList(Resource):

    @api_namespace.doc('list_drivers')
    @api_namespace.marshal_with(driver_model, as_list=True)
    @api_namespace.expect(search_parser)
    def get(self):
        '''
        Serarches for drivers using the routecode
        '''
        args = search_parser.parse_args()
        search_param = args['search']
        query = DriverModel.query
        if search_param:
            param = f'%{search_param}%'
            query = (query.filter(DriverModel.route.ilike(param)))
            # Old code, that it's not case insensitive in postgreSQL
            # query = (query.filter(DriverModel.text.contains(search_param)))

        query = query.order_by('id')
        drivers = query.all()

        return drivers


update_parser = authentication_parser.copy()
update_parser.add_argument('firstname', type=str, required=False,
                           help='Driver First Name')
update_parser.add_argument('lastname', type=str, required=False,
                           help='Driver Last Name')
update_parser.add_argument('residentialaddress', type=str,
                           required=False,
                           help=('Residential Address of the Bus'
                                 'Assistant'))
update_parser.add_argument('email', type=str, required=False,
                           help='Email Address of the Driver')
update_parser.add_argument('phoneno', type=str, required=False,
                           help="Driver's Phone Number")
update_parser.add_argument('operatorid', type=str, required=False,
                           help='The Driver Operator id')
update_parser.add_argument('bankname', type=str, required=False,
                           help='Driver bank name')
update_parser.add_argument('accountname', type=str, required=False,
                           help='Driver Account name')
update_parser.add_argument('license', type=str, required=False,
                           help='The driver license link')
update_parser.add_argument('accountnumber', type=str, required=False,
                           help='Driver Account number')
update_parser.add_argument('zone', type=str, required=False,
                           help='Driver zone')
update_parser.add_argument('area', type=str, required=False,
                           help='Driver area')
update_parser.add_argument('route', type=str, required=False,
                           help='Driver route')
update_parser.add_argument('geofencedarea', type=str, required=False,
                           help='Driver geo fenced area')


@api_namespace.route('/drivers/<int:driver_id>/')
class DriversRetrieve(Resource):

    @api_namespace.doc('retrieve_driver')
    @api_namespace.marshal_with(driver_model)
    def get(self, driver_id):
        '''
        Retrieve a driver using Id
        '''
        driver = DriverModel.query.get(driver_id)
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        return driver

    @api_namespace.doc('update_driver')
    @api_namespace.marshal_with(driver_model)
    @api_namespace.expect(update_parser)
    def put(self, driver_id):
        '''
        update a driver
        '''
        args = update_parser.parse_args()
        authentication_header_parser(args['Authorization'])
        driver = (
            DriverModel
            .query
            .filter(DriverModel.id == driver_id)
            .first()
        )
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        driver.firstname = args['firstname']
        driver.lastname = args['lastname']
        driver.residentialaddress = args['residentialaddress']
        driver.timestamp = datetime.now()
        driver.email = args['email']
        driver.phoneno = args['phoneno']
        driver.bankname = args['bankname']
        driver.operatorid = args['operatorid']
        driver.accountname = args['accountname']
        driver.accountnumber = args['accountnumber']
        driver.license = args['license']

        driver.zone = args['zone']
        driver.area = args['area']
        driver.route = args['route']
        driver.geofencedarea = args['geofencedarea']

        db.session.add(driver)
        db.session.commit()

        return driver


status_parser = api_namespace.parser()
status_parser.add_argument('status', type=str, required=True,
                           help='The driver status')


@api_namespace.route('/status/')
class DriversStatus(Resource):

    @api_namespace.doc('retrieve_driver')
    @api_namespace.marshal_with(driver_model, as_list=True)
    @api_namespace.expect(status_parser)
    def get(self):
        '''
        retrive driver with specified status
        '''
        args = status_parser.parse_args()
        status = args['status']
        driver = (
            DriverModel
            .query
            .filter(DriverModel.status == status)
            .all()
        )
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        return driver


@api_namespace.route('/status/<int:driver_id>/')
class DriversStatusUpdate(Resource):

    @api_namespace.doc('update_driver_status')
    @api_namespace.marshal_with(driver_model)
    @api_namespace.expect(status_parser)
    def put(self, driver_id):
        '''
        set the driver status
        '''
        args = status_parser.parse_args()
        status = args['status']
        driver = (
            DriverModel
            .query
            .filter(DriverModel.id == driver_id)
            .first()
        )
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        driver.status = status
        driver.approvedtimestamp = datetime.now()

        db.session.add(driver)
        db.session.commit()

        return driver


@api_namespace.route('/all/drivers/')
class AllDriverList(Resource):

    @api_namespace.doc('list_drivers')
    @api_namespace.marshal_with(driver_model, as_list=True)
    @api_namespace.expect(authentication_parser)
    def get(self):
        '''
        Retrieves all drivers
        '''
        args = authentication_parser.parse_args()
        authentication_header_parser(args['Authorization'])
        drivers = (
            DriverModel
            .query
            .order_by('id')
            .all()
        )

        return drivers


appstatus_parser = api_namespace.parser()
appstatus_parser.add_argument('status', type=str, required=True,
                              help='The driver app/online status')


@api_namespace.route('/appstatus/')
class DriversAppStatus(Resource):

    @api_namespace.doc('retrieve_driver')
    @api_namespace.marshal_with(driver_model, as_list=True)
    @api_namespace.expect(appstatus_parser)
    def get(self):
        '''
        retrive driver with specified online/app status
        '''
        args = appstatus_parser.parse_args()
        status = args['status']
        driver = (
            DriverModel
            .query
            .filter(DriverModel.appstatus == status)
            .all()
        )
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        return driver


@api_namespace.route('/appstatus/<int:driver_id>/')
class DriversAppStatusUpdate(Resource):

    @api_namespace.doc('update_driver_status')
    @api_namespace.marshal_with(driver_model)
    @api_namespace.expect(appstatus_parser)
    def put(self, driver_id):
        '''
        set the driver online status on the app
        '''
        args = appstatus_parser.parse_args()
        status = args['status']
        driver = (
            DriverModel
            .query
            .filter(DriverModel.id == driver_id)
            .first()
        )
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        driver.appstatus = status

        db.session.add(driver)
        db.session.commit()

        return driver


email_parser = api_namespace.parser()
email_parser.add_argument('email', type=str, required=True,
                          help='The driver email')


@api_namespace.route('/email/')
class DriversEmail(Resource):

    @api_namespace.doc('retrieve_driver')
    @api_namespace.marshal_with(driver_model, as_list=True)
    @api_namespace.expect(email_parser)
    def get(self):
        '''
        retrive driver with the driver email
        '''
        args = email_parser.parse_args()
        email = args['email']
        driver = (
            DriverModel
            .query
            .filter(
                func.lower(
                    DriverModel.email
                    )
                == func.lower(email)
                )
            .first()

        )
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        return driver


operator_parser = authentication_parser.copy()
operator_parser.add_argument('operatorid', type=str, required=False,
                             help='The driver operatorid')


@api_namespace.route('/drivers/operator/')
class OperatorDrivers(Resource):

    @api_namespace.doc('retrieve_driver')
    @api_namespace.marshal_with(driver_model)
    @api_namespace.expect(operator_parser)
    def get(self):
        '''
        Retrieve an operators driver's using operator Id
        '''
        args = operator_parser.parse_args()
        authentication_header_parser(args['Authorization'])
        operator = args['operatorid']
        drivers = (
            DriverModel
            .query
            .filter(DriverModel.operatorid == operator)
            .all()
        )
        if not drivers:
            # The driver is not present
            return '', http.client.NOT_FOUND

        return drivers


accept_parser = authentication_parser.copy()
accept_parser.add_argument('status', type=str, required=False,
                           help='the status value(code) for acceptance')
accept_parser.add_argument('operatorid', type=str, required=False,
                           help='the operator id')
accept_parser.add_argument('route', type=str, required=False,
                           help='The driver assigned route')


@api_namespace.route('/driver/operator/<int:driver_id>/')
class UpdateOperator(Resource):
    @api_namespace.doc('update_driver_status')
    @api_namespace.marshal_with(driver_model)
    @api_namespace.expect(accept_parser)
    def put(self, driver_id):
        '''
        update driver acceptance status
        the operator field can be ignored if the request was direct
        or previously accepted
        '''
        args = accept_parser.parse_args()
        authentication_header_parser(args['Authorization'])

        status = args['status']
        operator = args['operatorid']
        route = args['route']
        driver = (
            DriverModel
            .query
            .filter(DriverModel.id == driver_id)
            .first()
        )
        if not driver:
            # The driver is not present
            return '', http.client.NOT_FOUND

        driver.acceptstatus = status
        if operator:
            driver.operatorid = operator
        if route:
            driver.route = route

        driver.accepttimestamp = datetime.now()

        db.session.add(driver)
        db.session.commit()

        data = {
            'username': driver.usernamemain,
            'route': route,
            'operatorId': operator,
            'recieverEmail': driver.email,
            'recieverNo': driver.phoneno,
            'firstName': driver.firstname
        }

        # Create a new thrad and make request
        request = make_request(DRIVER_MSG_URL, data)
        request.start()

        driver = api_namespace.marshal(driver, driver_model)

        return driver


@api_namespace.route('/request/')
class DriverListRequests(Resource):

    @api_namespace.doc('list_drivers')
    @api_namespace.marshal_with(driver_model, as_list=True)
    @api_namespace.expect(operator_parser)
    def get(self):
        '''
        Retrieves request to all operators or specific operator
        If operator isn't specified, it shows request to all operators.
        If operator is specified, it shows request to that operator.
        '''
        args = operator_parser.parse_args()
        authentication_header_parser(args['Authorization'])
        operator = args['operatorid']
        query = (DriverModel.query)

        if operator:
            drivers = (
                query
                .filter(func.lower(DriverModel.operatorid)
                        ==
                        func.lower(operator)
                        )
                .filter(DriverModel.acceptstatus == '0')
                .order_by('timestamp')
                .all()
            )
        else:
            drivers = (
                query
                .filter(DriverModel.operatorid == None)
                .filter(DriverModel.acceptstatus == '0')
                .order_by('timestamp')
                .all()
            )

        return drivers


dateQuery_parser = authentication_parser.copy()
dateQuery_parser.add_argument('startdate', type=str, required=True,
                              help="The start date format '%d/%m/%Y'")
dateQuery_parser.add_argument('enddate', type=str, required=True,
                              help="The end date format '%d/%m/%Y'")


@api_namespace.route('/datequery/')
class DriversDateQuery(Resource):

    @api_namespace.doc('query count in db')
    @api_namespace.expect(dateQuery_parser)
    def get(self):
        '''
        Help find  the daily signup within a range of dates
        '''
        args = dateQuery_parser.parse_args()
        authentication_header_parser(args['Authorization'])

        start_date_str = args['startdate']
        end_date_str = args['enddate']

        start_date = datetime.strptime(start_date_str, "%d/%m/%Y").date()

        end_date = datetime.strptime(end_date_str, "%d/%m/%Y").date()

        result = {}

        if start_date > end_date:
            return '', http.client.BAD_REQUEST

        while start_date <= end_date:

            driver = (
                db.session
                .query(func.count(DriverModel.id))
                .filter(func.date(DriverModel.timestamp) == start_date)
                .all()
            )
            date = start_date.strftime("%d/%m/%Y")
            result[date] = driver[0][0]

            start_date = start_date + timedelta(days=1)

        return result


@api_namespace.route('/sumquery/')
class DriversSummaryQuery(Resource):

    @api_namespace.doc('query count in db')
    @api_namespace.expect(authentication_parser)
    def get(self):
        '''
        Help find total records in database
        '''
        args = authentication_parser.parse_args()
        authentication_header_parser(args['Authorization'])
        driver = (
                DriverModel
                .query
                .count()
            )

        return driver
