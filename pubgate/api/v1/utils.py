

def deliver(activity, recipients):
    # TODO deliver
    # TODO sign object
    pass


def make_label(activity):
    label = activity["type"]
    if isinstance(activity["object"], dict):
        label = f'{label}: {activity["object"]["type"]}'
    return label
