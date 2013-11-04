"""
Eucalyptus and AWS Instance models and constants

"""
from ..constants.instances import AWS_INSTANCE_TYPES


class Instance(object):
    """Eucalyptus or AWS Instance"""
    STATUS_CHOICES = ('Running', 'Stopped', 'Stopping', 'Pending', 'Terminating', 'Terminated')

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

    @classmethod
    def fakeall(cls, availability_zone=None):
        """Fake fetching a bunch of instances from an availability zone, for prototyping purposes.
        FIXME: Remove me after we're done prototyping
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from random import choice, randint
        from string import letters

        instances = []
        count = 100

        if availability_zone is None:
            availability_zone = 'PART01'

        for idx in xrange(count):
            instance_name = 'Instance_{0}'.format(''.join(choice(letters).lower() for i in range(6)))
            instance_id = 'i-{0}'.format(randint(11111111, 99999999))
            launch_time = datetime.today() - relativedelta(days=randint(1, 30))
            root_device = 'volume-{0}'.format(randint(1, 10))
            instances.append(dict(
                instance_id=instance_id,
                instance_name=instance_name,
                root_device=root_device,
                launch_time=launch_time.isoformat(),
                security_group='default',
                instance_type=choice(AWS_INSTANCE_TYPES),
                availability_zone=availability_zone,
                status=choice(cls.STATUS_CHOICES),
            ))
        return instances
