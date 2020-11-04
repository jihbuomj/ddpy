import os
import boto3

def update_domains(ip, config):
    route53 = boto3.client(
            'route53',
            aws_access_key_id=os.environ.get('DDPY_AWS_ACCESS_KEY'),
            aws_secret_access_key=os.environ.get('DDPY_AWS_SECRET_ACCESS_KEY')
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

            changes = [record_set_map(domain, ip) for domain in config['domains']]
            change_batch = {
                    'Changes': changes,
                    'Comment': 'Changes made from ddpy'
            }
            # response = route53.change_resource_record_sets(
            #         ChangeBatch=change_batch,
            #         HostedZoneId=zone['Id']
            # )
            break
