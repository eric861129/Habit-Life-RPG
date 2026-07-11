targetScope = 'subscription'

@minLength(3)
@maxLength(18)
param prefix string

param location string
param allowedOrigins string
param sqlAdministratorLogin string

@secure()
param sqlAdministratorPassword string

@secure()
param jwtSecret string

param tags object = {
  project: 'habit-life-rpg'
  environment: 'book-demo'
  costPolicy: 'zero-cost-only'
}

var resourceGroupName = '${prefix}-rg'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module database 'modules/sql-free-database.bicep' = {
  name: 'sql-free-database'
  scope: resourceGroup
  params: {
    prefix: prefix
    location: location
    administratorLogin: sqlAdministratorLogin
    administratorPassword: sqlAdministratorPassword
    tags: tags
  }
}

module backend 'modules/app-service.bicep' = {
  name: 'app-service'
  scope: resourceGroup
  params: {
    prefix: prefix
    location: location
    allowedOrigins: allowedOrigins
    databaseHost: database.outputs.databaseHost
    databaseName: database.outputs.databaseName
    databaseUser: sqlAdministratorLogin
    databasePassword: sqlAdministratorPassword
    jwtSecret: jwtSecret
    tags: tags
  }
}

module frontend 'modules/static-web-app.bicep' = {
  name: 'static-web-app'
  scope: resourceGroup
  params: {
    prefix: prefix
    location: location
    tags: tags
  }
}

output resourceGroupName string = resourceGroup.name
output frontendHostname string = frontend.outputs.defaultHostname
output backendHostname string = backend.outputs.defaultHostname
output backendHealthUrl string = 'https://${backend.outputs.defaultHostname}/health/live'
output backendDocsUrl string = 'https://${backend.outputs.defaultHostname}/docs'
output sqlServerName string = database.outputs.serverName
