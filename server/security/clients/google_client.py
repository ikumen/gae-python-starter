import jwt

from ..core import OAuth2Client, UnauthorizedException

class GoogleClient(OAuth2Client):
    """OAuthClient implementation that interacts with Google OAuth services.
    """
    def parse_token_response(self, oauth_resp):
        """Parses the OAuth response from Google and tries
        to parse out the email and access token.
        """
        if oauth_resp and 'id_token' in oauth_resp:
            userinfo = jwt.decode(oauth_resp['id_token'], verify=False)
            if 'email' in userinfo:
                return (userinfo['email'], dict(
                    token_type=oauth_resp['token_type'],
                    refresh_token=oauth_resp['refresh_token'] \
                        if 'refresh_token' in oauth_resp else None,
                    access_token=oauth_resp['access_token']))
            
        raise UnauthorizedException('Failed to parse response from provider: {}'\
            .format(self.config.get('ID')))
                