param prefix string
param location string
param administratorLogin string

@secure()
param administratorPassword string

param tags object

resource server 'Microsoft.Sql/servers@2023-08-01-preview' = {
  name: '${prefix}-sql'
  location: location
  properties: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorPassword
    minimalTlsVersion: '1.2'
    publicNetworkAccess: 'Enabled'
    restrictOutboundNetworkAccess: 'Disabled'
  }
  tags: tags
}

resource allowAzureServices 'Microsoft.Sql/servers/firewallRules@2023-08-01-preview' = {
  parent: server
  name: 'AllowAzureServices'
  properties: {
    startIpAddress: '0.0.0.0'
    endIpAddress: '0.0.0.0'
  }
}

resource database 'Microsoft.Sql/servers/databases@2025-01-01' = {
  parent: server
  name: 'habit-life-rpg'
  location: location
  sku: {
    name: 'GP_S_Gen5'
    tier: 'GeneralPurpose'
    family: 'Gen5'
    capacity: 2
  }
  properties: {
    autoPauseDelay: 60
    freeLimitExhaustionBehavior: 'AutoPause'
    licenseType: 'LicenseIncluded'
    maxSizeBytes: 34359738368
    minCapacity: json('0.5')
    readScale: 'Disabled'
    requestedBackupStorageRedundancy: 'Local'
    useFreeLimit: true
    zoneRedundant: false
  }
  tags: tags
}

output databaseHost string = server.properties.fullyQualifiedDomainName
output databaseName string = database.name
output serverName string = server.name
