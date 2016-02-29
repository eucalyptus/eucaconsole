from arn import AmazonResourceName, ServiceNamespace


@ServiceNamespace('autoscaling')
class AutoScaling(AmazonResourceName):
    """AmazonResourceName for AutoScaling namespace."""

    def __init__(self, arn=None):
        self.resource_type = None
        self.autoscaling_group_name = None
        self.policy_name = None
        self.policy_id = None
        self.group_id = None

        super(AutoScaling, self).__init__(arn)

    def parse(self, arn):
        resource = super(AutoScaling, self).parse(arn)
        (resource_type, id, names) = resource.split(':', 2)

        self.resource_type = resource_type
        names_dict = dict(pair.split('/') for pair in names.split(':'))
        self.autoscaling_group_name = names_dict.get('autoScalingGroupName')
        self.policy_name = names_dict.get('policyName')

        if resource_type == 'scalingPolicy':
            self.policy_id = id
        else:
            self.group_id = id
