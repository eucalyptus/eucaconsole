"""
Eucalyptus and AWS Launch Configuration models

"""
from boto.ec2.launchspecification import LaunchSpecification


class LaunchConfiguration(LaunchSpecification):
    """Eucalyptus or AWS launch configuration"""

    # TODO: Remove after we're done prototyping
    @classmethod
    def fakeall(cls):
        """Fake fetching a bunch of launch configurations for prototyping purposes.
        """
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        from random import choice, randint
        from string import letters

        items = []
        count = 40

        for idx in xrange(count):
            random_chars = ''.join(choice(letters).lower() for i in range(6))
            name = 'launchcfg-{0}'.format(random_chars)
            image = 'i-{0}'.format(random_chars)
            key = 'key-{0}'.format(choice(['one', 'two', 'three']))
            security_group = 'sgroup-{0}'.format(choice(['foo', 'bar', 'baz']))
            create_time = datetime.today() - relativedelta(days=randint(1, 30))
            block_device_mappings = [
                dict(device_mapping='device01', snapshot='snap01', size='128', delete_on_terminate=False)
            ]
            items.append(dict(
                name=name,
                image=image,
                key=key,
                security_group=security_group,
                create_time=create_time.isoformat(),
                block_device_mappings=block_device_mappings,
            ))
        return items
