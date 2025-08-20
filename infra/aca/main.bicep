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

// Variables
var containerAppsEnvironmentName = 'fire-iot-${environment}'
var appNamePrefix = 'app-${environment}'
var vnetName = 'fire-iot-vnet-${environment}'
var subnetName = 'container-apps-subnet'

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
        name: subnetName
        properties: {
          addressPrefix: '10.0.1.0/24'
          delegations: [
            {
              name: 'delegation'
              properties: {
                serviceName: 'Microsoft.App/containerApps'
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
    maximumThroughputUnits: 1
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

// PostgreSQL Server
resource postgresServer 'Microsoft.DBforPostgreSQL/flexibleServers@2023-06-01-preview' = {
  name: 'fire-iot-postgres-${environment}'
  location: location
  sku: {
    name: 'Standard_B1ms'
    tier: 'Burstable'
  }
  properties: {
    administratorLogin: postgresAdminUsername
    administratorLoginPassword: postgresAdminPassword
    version: '14'
    storage: {
      storageSizeGB: 32
    }
    network: {
      delegatedSubnetResourceId: vnet.properties.subnets[0].id
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

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerAppsEnvironmentName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    vnetConfiguration: {
      infrastructureSubnetId: vnet.properties.subnets[0].id
    }
  }
}

// ControlTower Container App
resource controlTowerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appNamePrefix}-controltower'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
      }
      secrets: [
        {
          name: 'postgres-connection'
          value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/fireiot'
        }
        {
          name: 'eventhub-connection'
          value: eventHubAuthRule.listKeys().primaryConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'controltower'
          image: '${dockerHubOrg}/controltower:${imageTag}'
          env: [
            {
              name: 'SPRING_PROFILES_ACTIVE'
              value: 'cloud'
            }
            {
              name: 'POSTGRES_URL'
              secretRef: 'postgres-connection'
            }
            {
              name: 'EVENTHUB_CONNECTION_STRING'
              secretRef: 'eventhub-connection'
            }
            {
              name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
              value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

// FacilityManagement Container App
resource facilityManagementApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appNamePrefix}-facilitymanagement'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
      }
      secrets: [
        {
          name: 'postgres-connection'
          value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/fireiot'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'facilitymanagement'
          image: '${dockerHubOrg}/facilitymanagement:${imageTag}'
          env: [
            {
              name: 'SPRING_PROFILES_ACTIVE'
              value: 'cloud'
            }
            {
              name: 'POSTGRES_URL'
              secretRef: 'postgres-connection'
            }
            {
              name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
              value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

// DataLake Container App
resource dataLakeApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appNamePrefix}-datalake'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: false
      }
      secrets: [
        {
          name: 'postgres-connection'
          value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/fireiot'
        }
        {
          name: 'redis-connection'
          value: 'redis://${redisCache.properties.hostName}:6380'
        }
        {
          name: 'eventhub-connection'
          value: eventHubAuthRule.listKeys().primaryConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'datalake'
          image: '${dockerHubOrg}/datalake:${imageTag}'
          env: [
            {
              name: 'PROFILE'
              value: 'cloud'
            }
            {
              name: 'POSTGRES_URL'
              secretRef: 'postgres-connection'
            }
            {
              name: 'REDIS_URL'
              secretRef: 'redis-connection'
            }
            {
              name: 'EVENTHUB_CONN'
              secretRef: 'eventhub-connection'
            }
            {
              name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
              value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
            }
          ]
          resources: {
            cpu: json('1.0')
            memory: '2Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

// Alert Container App
resource alertApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appNamePrefix}-alert'
  location: location
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: false  // Internal service
        targetPort: 8080
        allowInsecure: false
      }
      secrets: [
        {
          name: 'postgres-connection'
          value: 'postgresql://${postgresAdminUsername}:${postgresAdminPassword}@${postgresServer.properties.fullyQualifiedDomainName}:5432/fireiot'
        }
        {
          name: 'redis-connection'
          value: 'redis://${redisCache.properties.hostName}:6380'
        }
        {
          name: 'eventhub-connection'
          value: eventHubAuthRule.listKeys().primaryConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'alert'
          image: '${dockerHubOrg}/alert:${imageTag}'
          env: [
            {
              name: 'PROFILE'
              value: 'cloud'
            }
            {
              name: 'POSTGRES_URL'
              secretRef: 'postgres-connection'
            }
            {
              name: 'REDIS_URL'
              secretRef: 'redis-connection'
            }
            {
              name: 'EVENTHUB_CONN'
              secretRef: 'eventhub-connection'
            }
            {
              name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
              value: 'https://${appInsights.properties.InstrumentationKey}.live.applicationinsights.azure.com/v2.1/traces'
            }
          ]
          resources: {
            cpu: json('0.5')
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

// Outputs
output controlTowerUrl string = 'https://${controlTowerApp.properties.configuration.ingress.fqdn}'
output facilityManagementUrl string = 'https://${facilityManagementApp.properties.configuration.ingress.fqdn}'
output dataLakeUrl string = 'https://${dataLakeApp.properties.configuration.ingress.fqdn}'
output dockerHubOrg string = dockerHubOrg
output eventHubNamespace string = eventHubNamespace.name
output postgresServerFqdn string = postgresServer.properties.fullyQualifiedDomainName
output redisHostName string = redisCache.properties.hostName
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
