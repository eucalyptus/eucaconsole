class MetaARN(type):

    arn_types = []

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        mcs.arn_types.append(cls)
        return cls

    @classmethod
    def factory(meta, arn):
        (_, partition, service, _) = arn.split(':', 3)
        for arn_type in meta.arn_types:
            if arn_type.match(service):
                return arn_type(arn)


class ServiceNamespace(object):
    def __init__(self, arntype):
        self._arntype = arntype

    def __call__(self, cls):
        cls._arntype = self._arntype
        return cls


class AmazonResourceName(dict):
    __metaclass__ = MetaARN
    _arntype = None

    def __init__(self, arn=None):
        if arn is not None:
            self.parse(arn)

    def __str__(self):
        pass

    @classmethod
    def match(cls, service):
        return service == cls._arntype

    def parse(self, arn):
        (_, partition, service, region, accountid, resource) = arn.split(':', 5)

        self.partition = partition
        self.service = service
        self.region = region
        self.accountid = accountid

        return resource
