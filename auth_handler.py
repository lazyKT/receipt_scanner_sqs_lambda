import json


def authorizer (event, context):
    print(f'event: {event}')
    if 'authorization' not in event['headers'] or 'routeArn' not in event:
        return generate_auth_response('user', 'Deny', None)
    route_arn = event['routeArn']
    token = event['headers']['authorization']
    if token.lower() == 'allow':
        return generate_auth_response('user', 'Allow', route_arn)
    else:
        return generate_auth_response('user', 'Deny', route_arn)
    


def generate_auth_response (principal_id, effect, route_arn):
    policy_document = generate_policy_document (effect, route_arn)
    return {
        "principalId": principal_id,
        "policyDocument": policy_document
    }


def generate_policy_document (effect, route_arn):
    if effect is None or route_arn is None:
        return None
    return {
        "Version": '2012-10-17',
        'Statement': [{
            'Action': 'execute-api:Invoke',
            'Effect': effect,
            'Resource': route_arn
        }]
    }