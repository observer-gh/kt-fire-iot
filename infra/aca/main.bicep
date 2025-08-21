@description('The location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environment string = 'dev'

@description('Docker Hub organization name')
param dockerHubOrg string

@description('Image tag to deploy')
param imageTag string = 'latest'

@description('PostgreSQL admin username')
param postgresAdminUsername string = 'fireiot_admin'

@description('PostgreSQL admin password')
@secure()
param postgresAdminPassword string

@description('Event Hubs namespace name')
param eventHubNamespaceName string = 'fire-iot-eventhub-${environment}'

@description('Azure Computer Vision endpoint')
param azureVisionEndpoint string

@description('Azure Computer Vision API key')
@secure()
param azureVisionKey string

// Variables
var appNamePrefix = 'app-${environment}'
var vnetName = 'fire-iot-vnet-${environment}'
var containerAppsSubnetName = 'container-apps-subnet'
var postgresSubnetName = 'postgres-subnet'

// Virtual Network
resource vnet 'Microsoft.Network/virtualNetworks@2023-09-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: ['10.0.0.0/16']
    }
    subnets: [
      {
        name: containerAppsSubnetName
        properties: {
          addressPrefix: '10.0.1.0/24'
        }
      }
      {
        name: postgresSubnetName
        properties: {
          addressPrefix: '10.0.2.0/24'
          delegations: [
            {
              name: 'delegation'
              properties: {
                serviceName: 'Microsoft.DBforPostgreSQL/flexibleServers'
              }
            }
          ]
        }
      }
    ]
  }
}

// Note: Using Docker Hub instead of Azure Container Registry

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: 'fire-iot-appinsights-${environment}'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalyticsWorkspace.id
  }
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'fire-iot-logs-${uniqueString(resourceGroup().id)}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Event Hubs Namespace
resource eventHubNamespace 'Microsoft.EventHub/namespaces@2023-01-01-preview' = {
  name: eventHubNamespaceName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
    capacity: 1
  }
  properties: {
    zoneRedundant: false
    isAutoInflateEnabled: false
    maximumThroughputUnits: 0
  }
}

// // Event Hub Topics
resource sensorDataTopic 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'sensor-data'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 4
    status: 'Active'
  }
}

resource alertTopic 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'alerts'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 4
    status: 'Active'
  }
}

resource controlTopic 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'control-events'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 4
    status: 'Active'
  }
}

resource fireDetectionTopic 'Microsoft.EventHub/namespaces/eventhubs@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'rtVideoAnalysis.fireDetected'
  properties: {
    messageRetentionInDays: 7
    partitionCount: 4
    status: 'Active'
  }
}

// Event Hub Authorization Rule
resource eventHubAuthRule 'Microsoft.EventHub/namespaces/authorizationRules@2023-01-01-preview' = {
  parent: eventHubNamespace
  name: 'RootManageSharedAccessKey'
  properties: {
    rights: [
      'Listen'
      'Manage'
      'Send'
    ]
  }
}

// PostgreSQL Server for DataLake API
resource postgresDatalakeServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: 'fire-iot-postgres-datalake-${environment}'
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresAdminUsername
    administratorLoginPassword: postgresAdminPassword
    version: '16'
    storage: {
      storageSizeGB: 32
    }
    network: {
      delegatedSubnetResourceId: vnet.properties.subnets[1].id
      privateDnsZoneArmResourceId: privateDnsZone.id
    }
  }
}

// PostgreSQL Server for FacilityManagement
resource postgresFacilityManagementServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: 'fire-iot-postgres-facilitymanagement-${environment}'
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresAdminUsername
    administratorLoginPassword: postgresAdminPassword
    version: '16'
    storage: {
      storageSizeGB: 32
    }
    network: {
      delegatedSubnetResourceId: vnet.properties.subnets[1].id
      privateDnsZoneArmResourceId: privateDnsZone.id
    }
  }
}

// Private DNS Zone for PostgreSQL
resource privateDnsZone 'Microsoft.Network/privateDnsZones@2020-06-01' = {
  name: 'privatelink.postgres.database.azure.com'
  location: 'global'
  properties: {}
}

// Private DNS Zone VNet Link
resource privateDnsZoneVNetLink 'Microsoft.Network/privateDnsZones/virtualNetworkLinks@2020-06-01' = {
  parent: privateDnsZone
  name: 'fire-iot-link'
  location: 'global'
  properties: {
    registrationEnabled: false
    virtualNetwork: {
      id: vnet.id
    }
  }
}

// Redis Cache
resource redisCache 'Microsoft.Cache/redis@2023-08-01' = {
  name: 'fire-iot-redis-${environment}'
  location: location
  properties: {
    sku: {
      name: 'Basic'
      family: 'C'
      capacity: 0
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
  }
}



// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: 'fire-iot-plan-${environment}'
  location: location
  sku: {
    name: 'B3'
    tier: 'Basic'
  }
  properties: {
    reserved: true  // Linux
  }
}

// ControlTower Web App
resource controlTowerApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appNamePrefix}-controltower'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerHubOrg}/kt-fire-iot-controltower:${imageTag}'
      appSettings: [
        {
          name: 'SPRING_PROFILES_ACTIVE'
          value: 'cloud'
        }
        {
          name: 'EVENTHUB_CONNECTION_STRING'
          value: eventHubAuthRule.listKeys().primaryConnectionString
        }
        {
          name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
          value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8080'
        }
      ]
    }
  }
}

// FacilityManagement Web App
resource facilityManagementApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appNamePrefix}-facilitymanagement'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerHubOrg}/kt-fire-iot-facilitymanagement:${imageTag}'
      appSettings: [
        {
          name: 'SPRING_PROFILES_ACTIVE'
          value: 'cloud'
        }
        {
          name: 'POSTGRES_URL'
          value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresFacilityManagementServer.properties.fullyQualifiedDomainName}:5432/facilitymanagement'
        }
        {
          name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
          value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8080'
        }
      ]
    }
  }
}

// DataLake API Web App
resource dataLakeApiApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appNamePrefix}-datalake-api'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerHubOrg}/kt-fire-iot-datalake-api:${imageTag}'
      appSettings: [
        {
          name: 'PROFILE'
          value: 'cloud'
        }
        {
          name: 'POSTGRES_URL'
          value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresDatalakeServer.properties.fullyQualifiedDomainName}:5432/datalake'
        }
        {
          name: 'REDIS_URL'
          value: 'redis://${redisCache.properties.hostName}:6380'
        }

        {
          name: 'EVENTHUB_CONN'
          value: eventHubAuthRule.listKeys().primaryConnectionString
        }
        {
          name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
          value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8080'
        }
      ]
    }
  }
}

// DataLake Dashboard Web App
resource dataLakeDashboardApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appNamePrefix}-datalake-dashboard'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerHubOrg}/kt-fire-iot-datalake-dashboard:${imageTag}'
      appSettings: [
        {
          name: 'PROFILE'
          value: 'cloud'
        }
        {
          name: 'POSTGRES_URL'
          value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresDatalakeServer.properties.fullyQualifiedDomainName}:5432/datalake'
        }
        {
          name: 'REDIS_URL'
          value: 'redis://${redisCache.properties.hostName}:6380'
        }

        {
          name: 'EVENTHUB_CONN'
          value: eventHubAuthRule.listKeys().primaryConnectionString
        }
        {
          name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
          value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8501'
        }
      ]
    }
  }
}

// Alert Web App
resource alertApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appNamePrefix}-alert'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerHubOrg}/kt-fire-iot-alert:${imageTag}'
      appSettings: [
        {
          name: 'PROFILE'
          value: 'cloud'
        }
        {
          name: 'REDIS_URL'
          value: 'redis://${redisCache.properties.hostName}:6380'
        }
        {
          name: 'EVENTHUB_CONN'
          value: eventHubAuthRule.listKeys().primaryConnectionString
        }
        {
          name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
          value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8080'
        }
      ]
    }
  }
}

// Mock Server Web App
resource mockServerApp 'Microsoft.Web/sites@2023-01-01' = {
  name: '${appNamePrefix}-mock-server'
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'DOCKER|${dockerHubOrg}/kt-fire-iot-mock-server:${imageTag}'
      appSettings: [
        {
          name: 'PROFILE'
          value: 'cloud'
        }
        {
          name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
          value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
        }
        {
          name: 'WEBSITES_PORT'
          value: '8001'
        }
      ]
    }
  }
}

// Outputs
output controlTowerUrl string = 'https://${controlTowerApp.properties.defaultHostName}'
output facilityManagementUrl string = 'https://${facilityManagementApp.properties.defaultHostName}'
output dataLakeApiUrl string = 'https://${dataLakeApiApp.properties.defaultHostName}'
output dataLakeDashboardUrl string = 'https://${dataLakeDashboardApp.properties.defaultHostName}'
output alertUrl string = 'https://${alertApp.properties.defaultHostName}'
output mockServerUrl string = 'https://${mockServerApp.properties.defaultHostName}'
output dockerHubOrg string = dockerHubOrg
output eventHubNamespace string = eventHubNamespace.name
output postgresDatalakeServerFqdn string = postgresDatalakeServer.properties.fullyQualifiedDomainName
output postgresFacilityManagementServerFqdn string = postgresFacilityManagementServer.properties.fullyQualifiedDomainName
output redisHostName string = redisCache.properties.hostName
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
