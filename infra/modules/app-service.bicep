param prefix string
param location string
param allowedOrigins string
param databaseHost string
param databaseName string
param databaseUser string

@secure()
param databasePassword string

@secure()
param jwtSecret string

param tags object

resource plan 'Microsoft.Web/serverfarms@2025-03-01' = {
  name: '${prefix}-plan'
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
    capacity: 1
  }
  properties: {
    reserved: true
    zoneRedundant: false
  }
  tags: tags
}

resource app 'Microsoft.Web/sites@2025-03-01' = {
  name: '${prefix}-api'
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    publicNetworkAccess: 'Enabled'
    siteConfig: {
      alwaysOn: true
      appCommandLine: 'python -m alembic upgrade head && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000'
      ftpsState: 'Disabled'
      healthCheckPath: '/health/live'
      http20Enabled: true
      linuxFxVersion: 'PYTHON|3.12'
      minTlsVersion: '1.2'
    }
  }
  tags: tags
}

resource appSettings 'Microsoft.Web/sites/config@2025-03-01' = {
  parent: app
  name: 'appsettings'
  properties: {
    DATABASE_HOST: databaseHost
    DATABASE_NAME: databaseName
    DATABASE_USER: databaseUser
    DATABASE_PASSWORD: databasePassword
    HLR_ALLOWED_ORIGINS: allowedOrigins
    HLR_ENVIRONMENT: 'production'
    HLR_JWT_SECRET: jwtSecret
    SCM_DO_BUILD_DURING_DEPLOYMENT: 'true'
  }
}

resource ftpPolicy 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-04-01' = {
  parent: app
  name: 'ftp'
  properties: {
    allow: false
  }
}

resource scmPolicy 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-04-01' = {
  parent: app
  name: 'scm'
  properties: {
    allow: false
  }
}

output defaultHostname string = app.properties.defaultHostName
