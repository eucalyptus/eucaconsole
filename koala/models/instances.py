"""
Eucalyptus and AWS Instance models and constants

"""
from boto.ec2.instance import Instance as BotoInstance
from boto.ec2.instance import InstanceState as BotoInstanceState

from ..constants.instances import AWS_INSTANCE_TYPES


class InstanceState(BotoInstanceState):
    PENDING = 0
    RUNNING = 16
    SHUTTING_DOWN = 32  # Terminating
    TERMINATED = 48
    STOPPING = 64
    STOPPED = 80

    STATE_CHOICES = (
        (PENDING, 'Pending'),
        (RUNNING, 'Running'),
        (SHUTTING_DOWN, 'Terminating'),
        (TERMINATED, 'Terminated'),
        (STOPPING, 'Stopping'),
        (STOPPED, 'Stopped'),
    )


class Instance(BotoInstance):
    """Eucalyptus or AWS Instance"""
    INSTANCE_STATE_CHOICES = [val for key, val in InstanceState.STATE_CHOICES]

    @staticmethod
    def all(conn, instance_ids=None, filters=None, dry_run=False):
        """Get all instances given a connection object"""
        return conn.get_only_instances(instance_ids=instance_ids, filters=filters, dry_run=dry_run)

    @staticmethod
    def get_count_by_state(items=None, state=None):
        assert state and items
        return len([item for item in items if item.get('status') == state])

    # TODO: Remove after we're done prototyping
    @classmethod
    def fakeall(cls, availability_zone=None):
        """Fake fetching a bunch of instances from an availability zone, for prototyping purposes.
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from random import choice, randint
        from string import letters

        items = []
        count = 100

        if availability_zone is None:
            availability_zone = 'PART01'

        for idx in xrange(count):
            instance_name = 'Instance_{0}'.format(''.join(choice(letters).lower() for i in range(6)))
            instance_id = 'i-{0}'.format(randint(11111111, 99999999))
            launch_time = datetime.today() - relativedelta(days=randint(1, 30))
            root_device = 'volume-{0}'.format(randint(1, 10))
            items.append(dict(
                id=instance_id,
                name=instance_name,
                root_device=root_device,
                launch_time=launch_time.isoformat(),
                security_group='default',
                instance_type=choice(AWS_INSTANCE_TYPES),
                availability_zone=availability_zone,
                status=choice(cls.INSTANCE_STATE_CHOICES),
            ))
        return items
