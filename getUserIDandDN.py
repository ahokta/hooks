import requests
import json
import re
import csv

# Change this to Domain and APIKEY
oktadomain = 'https://<oktadomain>'
apikey = '<APIKEY>'
addomain = '<ADDOMAIN>' # use the value you see in "windowsDomainQualifiedName" if you check the AD group profile

# construct URLs
usersep = oktadomain + '/api/v1/users/'
groupsep = oktadomain + '/api/v1/groups?search=type eq "APP_GROUP" and profile.windowsDomainQualifiedName sw "' + addomain + '"'
headers = {'Authorization': 'SSWS ' + apikey}

# Get all users
u = requests.get(usersep, headers=headers)
# get all groups
g = requests.get(groupsep, headers=headers)

#
# functions
#
def composeCURL(userid):
    """This function compses the curl command to alter the user and make him use the hook the next time he logs in"""
    data = '{\"credentials\": {\"password\" : {\"hook\": {\"type\": \"default\"}}}}'
    curlcommand = "curl --request POST '" + usersep + userid +"' --header 'Accept: application/json' --header 'Content-Type: application/json' --header 'Authorization: SSWS " + apikey + "' --data-raw '" + data + "'"
    return (curlcommand)

# dnlist
dnList = []
auxiliaryList = []

# grouplist
groupList = []

users = json.loads(u.text)
groups = json.loads(g.text)

#############################################
#
# Get UserID and OUs
#
#############################################
# get ID and DN of users
for user in users:
    adDN = user.get('profile').get('adDN')
    if adDN is not None:
        noCN = re.sub(r'CN\=.+\,OU', 'OU', adDN)
        dnList.append(noCN)

# get only unique List of DNs
for dn in dnList:
    if dn not in auxiliaryList:
        auxiliaryList.append(dn)
# sort DNs
auxiliaryList.sort()

# Now read users again and list members of those OUs
# open csv file for OUgroups
# write DNs to CSV
# commands to alter users for Hooks to bash script
with open('MapOUsToGroups.csv', 'w') as file:
    writer = csv.writer(file)
    writer.writerow(["OU", "Members", "MemberIDs", "New Group in Okta"])
    for ouGroup in auxiliaryList:
        memberOfOUDNs = []
        memberOfOUIDs = []
        for user in users:
            adDN = user.get('profile').get('adDN')
            if adDN is not None:
                with open('AlterUsersForHook.sh', 'a') as curlfile:
                        curlfile.write(composeCURL(user.get('id')) + '\n')
                noCN = re.sub(r'CN\=.+\,OU', 'OU', adDN)
                if (ouGroup == noCN):
                    memberOfOUDNs.append(adDN)
                    memberOfOUIDs.append(user.get('id'))
        writer.writerow([ouGroup,memberOfOUDNs,memberOfOUIDs])



#############################################
#
# get AD Groups and their members
#
#############################################
# get names and DN for AD groups
with open('ADGroupsAndMembers.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(["Group", "Members"])
        for group in groups:
            memberList = []
            id = group.get('id')
            groupDN = group.get('profile').get('dn')

            # get members
            m = requests.get(usersep, headers=headers)
            members = json.loads(m.text)
            for member in members:
                memberID = member.get('id')
                memberList.append(memberID)

            if groupDN is not None:
                groupList.append(groupDN)
                writer.writerow([groupDN,memberList])
