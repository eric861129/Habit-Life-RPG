targetScope = 'subscription'

@minLength(3)
@maxLength(18)
param prefix string

param location string
param allowedOrigins string
param sqlAdministratorLogin string

@description('Set to true only after the image exists and Key Vault secrets have been populated.')
param deployContainerApp bool = false

@description('Immutable SHA tag or digest for the public book-demo API image.')
param containerImage string = 'ghcr.io/eric861129/habit-life-rpg-api:pending'

@secure()
param sqlAdministratorPassword string

@secure()
param jwtSecret string

param tags object = {
  project: 'habit-life-rpg'
  environment: 'book-demo'
  costPolicy: 'book-launch-budget-30-usd'
}

var resourceGroupName = '${prefix}-rg'

resource resourceGroup 'Microsoft.Resources/resourceGroups@2024-11-01' = {
  name: resourceGroupName
  location: location
  tags: tags
}

module costGuard 'modules/cost-guard.bicep' = {
  name: 'cost-guard'
  scope: resourceGroup
  params: {
    prefix: prefix
    tags: tags
  }
}

module database 'modules/sql-database.bicep' = {
  name: 'sql-database'
  scope: resourceGroup
  params: {
    prefix: prefix
    location: location
    administratorLogin: sqlAdministratorLogin
    administratorPassword: sqlAdministratorPassword
    tags: tags
  }
  dependsOn: [
    costGuard
  ]
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

module containerPlatform 'modules/container-app-platform.bicep' = {
  name: 'container-app-platform'
  scope: resourceGroup
  params: {
    prefix: prefix
    location: location
    tags: tags
  }
}

module containerBackend 'modules/container-app.bicep' = if (deployContainerApp) {
  name: 'container-app'
  scope: resourceGroup
  params: {
    prefix: prefix
    location: location
    environmentId: containerPlatform.outputs.environmentId
    runtimeIdentityId: containerPlatform.outputs.runtimeIdentityId
    keyVaultUri: containerPlatform.outputs.keyVaultUri
    containerImage: containerImage
    allowedOrigins: allowedOrigins
    databaseHost: database.outputs.databaseHost
    databaseName: database.outputs.databaseName
    databaseUser: sqlAdministratorLogin
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
output containerAppName string = deployContainerApp ? containerBackend!.outputs.name : ''
output containerBackendHostname string = deployContainerApp ? containerBackend!.outputs.defaultHostname : ''
output containerEnvironmentId string = containerPlatform.outputs.environmentId
output keyVaultName string = containerPlatform.outputs.keyVaultName
output runtimeIdentityId string = containerPlatform.outputs.runtimeIdentityId
output sqlServerName string = database.outputs.serverName
output budgetName string = costGuard.outputs.budgetName
output usd20AlertBudgetName string = costGuard.outputs.usd20AlertBudgetName
output actionGroupName string = costGuard.outputs.actionGroupName
