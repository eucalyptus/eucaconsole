"""
Eucalyptus and AWS Instance models and constants

"""
from ..constants.instances import AWS_INSTANCE_TYPES


class Instance(object):
    """Eucalyptus or AWS Instance"""
    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs.get('key'))

    def get(self, instance_id):
        """Get an instance given an ID"""
        # TODO: Implement
        raise NotImplementedError()

    @staticmethod
    def filter(**kwargs):
        """Get instances given one or more filter criteria"""
        # TODO: Implement
        raise NotImplementedError()

    @staticmethod
    def all(availability_zone=None):
        """Get all instances from an availability zone"""
        # TODO: Implement
        raise NotImplementedError()

    @staticmethod
    def fakeall(availability_zone=None):
        """Fake fetching a bunch of instances from an availability zone, for prototyping purposes.
        FIXME: Remove me after we're done prototyping
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from random import choice, randint

        instances = []
        count = 200
        status_choices = ('Running', 'Stopped', 'Stopping', 'Pending', 'Terminating', 'Terminated')

        if availability_zone is None:
            availability_zone = 'PART01'

        for idx in xrange(count):
            instance_name = 'Instance_{0:0d}'.format(idx + 1)
            instance_id = 'i-{}'.format(randint(11111111, 99999999))
            created_date = datetime.today() - relativedelta(days=randint(1, 30))
            instances.append(dict(
                instance_name=instance_name,
                instance_id=instance_id,
                created_date=created_date.isoformat(),
                security_group='default',
                instance_type=choice(AWS_INSTANCE_TYPES),
                availability_zone=availability_zone,
                status=choice(status_choices),
            ))
        return instances
