"""
Models for Eucalyptus and AWS security groups

"""
from boto.ec2.securitygroup import SecurityGroup as BotoSecurityGroup


class SecurityGroup(BotoSecurityGroup):
    """Eucalyptus or AWS Security Group"""

    # TODO: Remove after we're done prototyping
    @staticmethod
    def fakeall():
        """Fake fetching a bunch of security groups for prototyping purposes.
        """
        from random import choice
        from string import letters

        items = []
        count = 10

        for idx in xrange(count):
            name = 'sgroup_{0}'.format(''.join(choice(letters).lower() for i in range(6)))
            description = 'description for {0}'.format(name)
            tags = [dict(key='foo', value='bar'), dict(key='baz', value='bat'), dict(key='biz', value='buz')]
            items.append(dict(
                name=name,
                description=description,
                tags=tags,
            ))
        return items
