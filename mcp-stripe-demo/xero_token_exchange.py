from xero.auth import OAuth2Credentials

# After receiving the authorization code from the redirect
authorization_code = "AUTHORIZATION_CODE_FROM_REDIRECT"

credentials = OAuth2Credentials(client_id, client_secret, redirect_uri)
credentials.verify(request_token=authorization_code)

# Now you can use the access token to make API calls
print("Access Token:", credentials.access_token)
print("Refresh Token:", credentials.refresh_token)
