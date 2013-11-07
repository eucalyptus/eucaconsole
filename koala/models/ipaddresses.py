"""
Models for Eucalyptus and AWS IP Addresses

"""
from boto.ec2.address import Address


class IPAddress(Address):
    """Eucalyptus or AWS Elastic IP Address"""

    # TODO: Remove after we're done prototyping
    @staticmethod
    def fakeall():
        """Fake fetching a bunch of IP addresses for prototyping purposes.
        """
        from random import choice
        from string import letters

        items = []
        count = 10

        for idx in xrange(count):
            ip_address = '10.101.50.{0}'.format(choice(range(255)) + 1)
            instance = 'instance_{0}'.format(''.join(choice(letters).lower() for i in range(6)))
            items.append(dict(
                ip_address=ip_address,
                instance=instance,
            ))
        return items
