import boto3
import boto3.session
import pprint

# TODO: profile as parameter of script
dev = boto3.session.Session(profile_name='dev')

ecs = dev.client('ecs')

# TODO: nextToken iteration for >100 clusters
clusters = ecs.list_clusters()['clusterArns']

clusterNames = list()
for name in map(lambda arn: arn.split("/")[1], clusters):
    clusterNames.append(name)

print("Current clusters in dev profile:")
pprint.pprint(clusterNames)

print("-----------------------------")

# TODO: nextToken iteration for >10 capacity providers
capacity_providers = ecs.describe_capacity_providers()['capacityProviders']

IGNORE_NAMES = ["FARGATE", "FARGATE_SPOT"]

capacity_providers_to_delete = list()
for capacity_provider in capacity_providers:
    if capacity_provider['name'] in IGNORE_NAMES:
        continue

    if capacity_provider['name'] not in clusterNames:
        capacity_providers_to_delete.append(capacity_provider['capacityProviderArn'])

print("Capacity providers to be deleted:")
for capacity_provider_arn in capacity_providers_to_delete:
    print(capacity_provider_arn)

print("-----------------------------")

s = input("Do you want to continue? [y|N]")
if s != "y":
    print("Exiting...")
    exit(-1)

'''
We had issues with capacity providers which were sort of dangling.
They had DELETE_FAILED, beacuse of association with a cluster,
but there was no cluster anymore. Do remidy this problem, create a cluster
attach the capacity provider via CLI/API and delete the capacity provider.
It will still say DELETE_FAILED, but then be gone. Delete the cluster afterwards.
'''
#print("Trying to disassociate capacity providers first.")

#for name in map(lambda arn: arn.split("/")[1], capacity_providers_to_delete):
#    deassociate_resp = ecs.put_cluster_capacity_providers(cluster=name, capacityProviders=[], defaultCapacityProviderStrategy=[])
#    print(deassociate_resp)
    
print("Deleting capacity providers.")
for capacity_provider_arn in capacity_providers_to_delete:
    del_resp = ecs.delete_capacity_provider(capacityProvider=capacity_provider_arn)
    print("got", del_resp['capacityProvider']['updateStatus'], "for", capacity_provider_arn, "(reason:", del_resp['capacityProvider']['updateStatusReason'], ")")