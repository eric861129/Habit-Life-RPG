param prefix string
param location string
param tags object

resource frontend 'Microsoft.Web/staticSites@2025-03-01' = {
  name: '${prefix}-web'
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    allowConfigFileUpdates: true
  }
  tags: tags
}

output defaultHostname string = frontend.properties.defaultHostname
