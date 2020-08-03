import http.client
from flask_restplus import Namespace, Resource
from drivers_backend.models import DriverModel
from drivers_backend.db import db

admin_namespace = Namespace('admin', description='Admin operations')


@admin_namespace.route('/drivers/<int:driver_id>/')
class DriversDelete(Resource):

    @admin_namespace.doc('delete_driver',
                         responses={http.client.NO_CONTENT: 'No content'})
    def delete(self, driver_id):
        '''
        Delete a driver
        '''
        driver = DriverModel.query.get(driver_id)
        if not driver:
            # The driver is not present
            return '', http.client.NO_CONTENT

        db.session.delete(driver)
        db.session.commit()

        return '', http.client.NO_CONTENT
