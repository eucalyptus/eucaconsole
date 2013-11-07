"""
Eucalyptus and AWS Volume models

"""
from boto.ec2.volume import Volume as BotoVolume
from boto.ec2.volume import AttachmentSet as BotoAttachmentSet


class AttachmentSet(BotoAttachmentSet):
    # NOTE: The ints here don't correspond to AWS volume attachment status codes,
    #       since there don't appear to be standard codes there (unlike in InstanceState).
    CREATING = 10
    CREATED = 20
    ATTACHING = 30
    ATTACHED = 40
    DETACHING = 50
    DETACHED = 60

    STATE_CHOICES = (
        (CREATING, 'Creating'),
        (CREATED, 'Created'),
        (ATTACHING, 'Attaching'),
        (ATTACHED, 'Attached'),
        (DETACHING, 'Detaching'),
        (DETACHED, 'Detached'),
    )


class Volume(BotoVolume):
    """Eucalyptus or AWS Volume"""
    VOLUME_STATE_CHOICES = [val for key, val in AttachmentSet.STATE_CHOICES]

    # TODO: Remove after we're done prototyping
    @classmethod
    def fakeall(cls, availability_zone=None):
        """Fake fetching a bunch of volumes for prototyping purposes.
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from random import choice, randint
        from string import letters

        items = []
        count = 40

        if availability_zone is None:
            availability_zone = 'cluster01'

        for idx in xrange(count):
            random_chars = ''.join(choice(letters).lower() for i in range(6))
            name = 'volume_{0}'.format(random_chars)
            volume_id = 'vol-{0}'.format(random_chars)
            create_time = datetime.today() - relativedelta(days=randint(1, 30))
            size = randint(2, 1024)  # GB
            tags = [dict(key='foo', value='bar'), dict(key='baz', value='bat'), dict(key='biz', value='buz')]
            instance = choice(['i-{0}'.format(random_chars), ''])
            snapshot = 'snap-{0}'.format(random_chars)
            items.append(dict(
                id=volume_id,
                name=name,
                size=size,
                instance=instance,
                snapshot=snapshot,
                tags=tags,
                create_time=create_time.isoformat(),
                availability_zone=availability_zone,
                status=choice(cls.VOLUME_STATE_CHOICES),
            ))
        return items
