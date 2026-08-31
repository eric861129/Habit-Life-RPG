param prefix string
param location string
param environmentId string
param runtimeIdentityId string
param keyVaultUri string
param containerImage string
param allowedOrigins string
param databaseHost string
param databaseName string
param databaseUser string
param tags object

resource api 'Microsoft.App/containerApps@2025-01-01' = {
  name: '${prefix}-api-ca'
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${runtimeIdentityId}': {}
    }
  }
  properties: {
    managedEnvironmentId: environmentId
    workloadProfileName: 'Consumption'
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        allowInsecure: false
        external: true
        targetPort: 8000
        transport: 'auto'
      }
      maxInactiveRevisions: 3
      secrets: [
        {
          name: 'database-password'
          keyVaultUrl: '${keyVaultUri}secrets/database-password'
          identity: runtimeIdentityId
        }
        {
          name: 'hlr-jwt-secret'
          keyVaultUrl: '${keyVaultUri}secrets/hlr-jwt-secret'
          identity: runtimeIdentityId
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'api'
          image: containerImage
          env: [
            {
              name: 'DATABASE_HOST'
              value: databaseHost
            }
            {
              name: 'DATABASE_NAME'
              value: databaseName
            }
            {
              name: 'DATABASE_USER'
              value: databaseUser
            }
            {
              name: 'DATABASE_PASSWORD'
              secretRef: 'database-password'
            }
            {
              name: 'HLR_ALLOWED_ORIGINS'
              value: allowedOrigins
            }
            {
              name: 'HLR_ENVIRONMENT'
              value: 'production'
            }
            {
              name: 'HLR_JWT_SECRET'
              secretRef: 'hlr-jwt-secret'
            }
          ]
          probes: [
            {
              type: 'Startup'
              httpGet: {
                path: '/health/live'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 2
              periodSeconds: 3
              timeoutSeconds: 2
              failureThreshold: 20
            }
            {
              type: 'Liveness'
              httpGet: {
                path: '/health/live'
                port: 8000
                scheme: 'HTTP'
              }
              periodSeconds: 30
              timeoutSeconds: 3
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health/ready'
                port: 8000
                scheme: 'HTTP'
              }
              periodSeconds: 15
              timeoutSeconds: 5
              failureThreshold: 6
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 2
        rules: [
          {
            name: 'http-concurrency'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
  tags: tags
}

output defaultHostname string = api.properties.configuration.ingress.fqdn
output name string = api.name
