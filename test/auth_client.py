import base64

import gssapi
import requests

test_protected = False

SPNEGO = gssapi.Mechanism.from_sasl_name("SPNEGO")

target = gssapi.Name("HTTP@api.drugguardian.net",
                     gssapi.NameType.hostbased_service)

ctx = gssapi.SecurityContext(name=target,
                             mech=SPNEGO,
                             usage="initiate")

in_token = None
out_token = ctx.step(in_token)


token = base64.b64encode(out_token).decode('utf-8')

print(token)

if test_protected:
    print("Testing protected")
    headers = {
        'Authorization': f'Negotiate {token}'
    }

    # Make the HTTP request
    url = "http://api.drugguardian.net/token"
    response = requests.get(url, headers=headers)

    print(response.headers)

    # Check the response
    if response.status_code == 200:
        print(response.json())
    else:
        print(f"Failed with status code: {response.status_code}")
        print(response.text)
