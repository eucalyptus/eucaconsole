"""
Eucalyptus and AWS snapshot models

"""
from boto.ec2.snapshot import Snapshot as BotoSnapshot


class SnapshotState(object):
    PENDING = 10
    COMPLETED = 20
    ERROR = 30

    STATE_CHOICES = (
        (PENDING, 'Pending'),
        (COMPLETED, 'Completed'),
        (ERROR, 'Failed'),
    )


class Snapshot(BotoSnapshot):
    """Eucalyptus or AWS Snapshot"""
    SNAPSHOT_STATE_CHOICES = [val for key, val in SnapshotState.STATE_CHOICES]

    # TODO: Remove after we're done prototyping
    @classmethod
    def fakeall(cls, availability_zone=None):
        """Fake fetching a bunch of snapshots for prototyping purposes.
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from random import choice, randint
        from string import letters

        items = []
        count = 40

        for idx in xrange(count):
            random_chars = ''.join(choice(letters).lower() for i in range(6))
            name = 'snapshot_{0}'.format(random_chars)
            description = 'description of {0}'.format(random_chars)
            snapshot_id = 'snap-{0}'.format(random_chars)
            start_time = datetime.today() - relativedelta(days=randint(1, 30))
            size = randint(2, 1024)  # GB
            tags = [dict(key='foo', value='bar'), dict(key='baz', value='bat'), dict(key='biz', value='buz')]
            volume = 'vol-{0}'.format(random_chars)
            snapshot = 'snap-{0}'.format(random_chars)
            items.append(dict(
                id=snapshot_id,
                name=name,
                description=description,
                size=size,
                volume=volume,
                snapshot=snapshot,
                tags=tags,
                start_time=start_time.isoformat(),
                status=choice(cls.SNAPSHOT_STATE_CHOICES),
            ))
        return items
