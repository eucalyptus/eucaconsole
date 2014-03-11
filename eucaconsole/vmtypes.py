# This code copied from boto, but the namespaces have been removed.
# we can revert this once boto gets updated. (working on a patch - dak)

from boto.ec2.ec2object import EC2Object


class VmType(EC2Object):
    """
    Represents an EC2 VM Type

    :ivar name: The name of the vm type
    :ivar cores: The number of cpu cores for this vm type
    :ivar memory: The amount of memory in megabytes for this vm type
    :ivar disk: The amount of disk space in gigabytes for this vm type
    """

    def __init__(self, connection=None, name=None, cores=None,
                 memory=None, disk=None):
        EC2Object.__init__(self, connection)
        self.connection = connection
        self.name = name
        self.cores = cores
        self.memory = memory
        self.disk = disk

    def __repr__(self):
        return 'VmType:%s-%s,%s,%s' % (self.name, self.cores,
                                       self.memory, self.disk)

    def endElement(self, name, value, connection):
        if name == 'name':
            self.name = value
        elif name == 'cpu':
            self.cores = value
        elif name == 'disk':
            self.disk = value
        elif name == 'memory':
            self.memory = value
        else:
            setattr(self, name, value)
