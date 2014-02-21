# -*- coding: utf-8 -*-
"""
Misc utility functions

"""


def show_resource_for_action(action):
    """Given an IAM policy action, determine if we should display the resource type/value selector"""
    hide_keywords = ['Account', 'Address', 'AvailabilityZone', 'Password', 'Placement', 'Region', 'Tag']
    for keyword in hide_keywords:
        if keyword in action:
            return False
    return True

