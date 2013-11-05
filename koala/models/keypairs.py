"""
Models for Eucalyptus and AWS key pairs

"""
from boto.ec2.keypair import KeyPair as BotoKeyPair


class KeyPair(BotoKeyPair):
    """Eucalyptus or AWS Key Pair"""

    # TODO: Remove after we're done prototyping
    @staticmethod
    def fakeall():
        """Fake fetching a bunch of key pairs for prototyping purposes.
        """
        import hashlib
        from random import choice
        from string import letters

        keypairs = []
        count = 10

        for idx in xrange(count):
            name = 'keypair_{0}'.format(''.join(choice(letters).lower() for i in range(6)))
            fingerprint = hashlib.md5(name).hexdigest()
            keypairs.append(dict(
                name=name,
                fingerprint=fingerprint,
            ))
        return keypairs
