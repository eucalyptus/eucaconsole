class MetaARN(type):
    """Metaclass for AmazonResourceName subclasses.

    MetaARN provides a factory method for AmazonResourceName.  All classes that
    inherit from AmazonResourceName will be cataloged by the metaclass, so no
    further management of the factory method is necessary.
    """

    arn_types = []

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        mcs.arn_types.append(cls)
        return cls

    @classmethod
    def factory(mcs, arn):
        """AmazonResourceName factory method.

        Given an ARN string provided by AWS or Euca, return an instance of the
        appropriate AmazonResourceName subclass.

        instance = AmazonResourceName.factory(<arn>)
        """
        (_, partition, service, _) = arn.split(':', 3)
        for arn_type in mcs.arn_types:
            if arn_type.match(service):
                return arn_type(arn)


class ServiceNamespace(object):
    """AmazonResourceName service namespace class decorator.

    Decorates AmazonResourceName subclasses with the matching AWS service namespace.

    http://docs.aws.amazon.com/general/latest/gr/aws-arns-and-namespaces.html#genref-aws-service-namespaces
    """
    def __init__(self, arntype):
        self._arntype = arntype

    def __call__(self, cls):
        cls._arntype = self._arntype
        return cls


class AmazonResourceName(dict):
    """Parse an Amazon Resource Name string into its component parts.

    Not to be instantiated directly, use the AmazonResourceName.factory() method
    to return an object of the correct type.
    """
    __metaclass__ = MetaARN
    _arntype = None

    def __init__(self, arn=None):
        self.arn = None
        self.partition = None
        self.service = None
        self.region = None
        self.accountid = None

        if arn is not None:
            self.parse(arn)

    def __str__(self):
        pass

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

    @classmethod
    def match(cls, service):
        """Match the ARN service namespace to the decorated ServiceNamespace."""
        return service == cls._arntype

    def parse(self, arn):
        (_, partition, service, region, accountid, resource) = arn.split(':', 5)

        self.arn = arn
        self.partition = partition
        self.service = service
        self.region = region
        self.accountid = accountid

        return resource
