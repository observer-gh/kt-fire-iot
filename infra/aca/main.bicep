@description('The name of the resource group')
param resourceGroupName string

@description('The location for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
param environment string = 'dev'

@description('Docker Hub organization name')
param dockerHubOrg string

@description('Image tag to deploy')
param imageTag string = 'latest'

@description('PostgreSQL connection string')
param postgresConnectionString string

@description('Redis connection string')
param redisConnectionString string

@description('Event Hubs connection string')
param eventHubConnectionString string

@description('OpenTelemetry endpoint')
param otelEndpoint string = ''

// Variables
var containerAppsEnvironmentName = 'fire-iot-${environment}'
var appNamePrefix = 'app-${environment}'

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
          value: postgresConnectionString
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
              name: 'OTEL_EXPORTER_OTLP_ENDPOINT'
              value: otelEndpoint
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

// StaticManagement Container App
resource staticManagementApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${appNamePrefix}-staticmanagement'
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
          value: postgresConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'staticmanagement'
          image: '${dockerHubOrg}/staticmanagement:${imageTag}'
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
              value: otelEndpoint
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
          value: postgresConnectionString
        }
        {
          name: 'redis-connection'
          value: redisConnectionString
        }
        {
          name: 'eventhub-connection'
          value: eventHubConnectionString
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
              value: otelEndpoint
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
          value: postgresConnectionString
        }
        {
          name: 'redis-connection'
          value: redisConnectionString
        }
        {
          name: 'eventhub-connection'
          value: eventHubConnectionString
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
              value: otelEndpoint
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
output staticManagementUrl string = 'https://${staticManagementApp.properties.configuration.ingress.fqdn}'
output dataLakeUrl string = 'https://${dataLakeApp.properties.configuration.ingress.fqdn}'
output logAnalyticsWorkspaceId string = logAnalyticsWorkspace.id
