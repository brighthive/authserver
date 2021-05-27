// This describes the Brighthive JWT.
// Many of these 'claims' are well-known and you can google about them.
// Claims preprended with 'brighthive' are unique to us.
{
  // these are claims that APIs care about
  "iss": "brighthive-authserver", // This is the service that issued the token
  "aud": [
    "brighthive-data-trust-manager",
    "brighthive-data-catalog-manager",
    "brighthive-governance-api",
    "brighthive-permissions-service",
    "brighthive-data-uploader-service",
    "brighthive-authserver"
  ], // This is an audience list. APIs will check if their name is listed here before accepting the JWT.
  "iat": 1621884448, // This is an issued at time. Access should not be granted before this time.
  "exp": 1623958048, // This is expiration time. Access should not be granted after this time.
  

  // These are the claims facet cares about!
  "brighthive-access-token": "2RjWW1X7mihQ9xA1GtC3iXF8ndu2xsZlD7lxQPUX5k"
  "brighthive-super-admin": true, // OPTIONAL! May or may not be present. This indicates if the user is a brighthive SuperAdmin
  
  "brighthive-org-role": {
    "organization-uuid": "admin",
    "organization-uuid": "user",
    "organization-uuid": "third-party",
  }, // Mandatory. 
  
  "brighthive-collaboration-role": {
    "collaboration-uuid": "admin",
    "collaboration-uuid": "user",
    "collaboration-uuid": "third-party"
  },

  "brighthive-data-resource-claims": {
    "data-resource-uuid": {
      "role": "Admin",
      "permissions": [
        "data:view",
        "data:download",
        "data:edit",
        "data-dict:view",
        "data-dict:download",
        "data-dict:edit"
      ]}
  }
}