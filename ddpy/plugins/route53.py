import os
import boto3

def update_domains(ip_info, config):
    if (
        'aws_access_key_id' in config
        and 'aws_secret_access_key' in config
    ):
        aws_access_key_id = config['aws_access_key_id']
        aws_secret_access_key = config['aws_secret_access_key']
    elif (
        'DDPY_AWS_ACCESS_KEY_ID' in os.environ
        and 'DDPY_AWS_SECRET_ACCESS_KEY' in os.environ
    ):
        aws_access_key_id = os.environ.get('DDPY_AWS_ACCESS_KEY_ID'),
        aws_secret_access_key = os.environ.get('DDPY_AWS_SECRET_ACCESS_KEY')
    else:
        aws_access_key_id = None
        aws_secret_access_key = None


    route53 = boto3.client(
            'route53',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
    )

    hosted_zones = route53.list_hosted_zones()['HostedZones']

    for zone in hosted_zones:
        if zone['Name'] == config['zone']:
            record_set_map = lambda domain, new_ip: {
                    'Action': 'UPSERT',
                    'ResourceRecordSet': {
                        'Name': domain,
                        'ResourceRecords': [
                            {
                                'Value': new_ip,
                            },
                        ],
                        'TTL': 60,
                        'Type': 'A',
                    },
            }

            changes = [record_set_map(domain, ip_info['ip']) for domain in config['domains']]

            if 'comment' in config:
                comment = config['comment']
            else:
                comment = 'Changes made by ddpy'

            change_batch = {
                    'Changes': changes,
                    'Comment': comment
            }
            route53.change_resource_record_sets(
                    ChangeBatch=change_batch,
                    HostedZoneId=zone['Id']
            )
            break
