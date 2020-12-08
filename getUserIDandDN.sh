#!/bin/bash

url=https://id3.antonherber.de/api/v1/users/
apikey=00CRx596VFz3Q39iK5ZnEYu5_xXHG9q9FJ3EvXZJrC
# just some url

curl --location --request GET ${url}  --header 'Accept: application/json' --header 'Content-Type: application/json' --header 'Authorization: SSWS ' ${apikey}