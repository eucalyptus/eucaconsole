"""
Eucalyptus and AWS Scaling Group models

"""
from boto.ec2.autoscale import AutoScalingGroup as BotoAutoScalingGroup


class AutoScalingGroup(BotoAutoScalingGroup):
    """Eucalyptus or AWS Auto-scaling Group"""

    # TODO: Remove after we're done prototyping
    @classmethod
    def fakeall(cls):
        """Fake fetching a bunch of scaling groups for prototyping purposes.
        """
        from random import choice, randint
        from string import letters

        items = []
        count = 40

        for idx in xrange(count):
            random_chars = ''.join(choice(letters).lower() for i in range(6))
            name = 'asgroup-{0}'.format(random_chars)
            launch_config = 'lconfig-{0}'.format(random_chars)
            availability_zones = ['cluster01', 'cluster02']
            instances = dict(current=3, desired=5, max=8, min=1)
            tags = [dict(key='foo', value='bar'), dict(key='baz', value='bat'), dict(key='biz', value='buz')]
            instance_health = choice(['All healthy', 'Unhealthy'])
            load_balancers = ['balancer01', 'balancer02']
            health_check = dict(type='EC2', grace_period=randint(120, 240))
            items.append(dict(
                name=name,
                tags=tags,
                launch_config=launch_config,
                instances=instances,
                instance_health=instance_health,
                status=instance_health,
                availability_zones=availability_zones,
                load_balancers=load_balancers,
                health_check=health_check,
            ))
        return items
