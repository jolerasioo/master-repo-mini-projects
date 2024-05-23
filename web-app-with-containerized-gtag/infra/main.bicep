/*
Bicep IaC template for deploying:
- One Azure App Service intance running .NET 6
- One Azure Container Environment
- Two Azure Container Apps
*/ 



param location string = resourceGroup().location

// app params
param webAppName string = uniqueString(resourceGroup().id) // Generate unique String for web app name
param sku string = 'F1' // The SKU of App Service Plan
param windowsFxV string = 'dotnet|6.0' // The runtime stack of web app

param hasGitRepo bool = false // if the web app has a git repository 
param repositoryUrl string // point to the repository of the web app
param branch string = 'main' // the branch of the repository

 // container apps params
@description('Specifies the name of the container app.')
param containerAppName string = 'gtm-${uniqueString(resourceGroup().id)}'

@description('Specifies the name of the container app environment.')
param containerAppEnvName string = 'containerapp-env-${uniqueString(resourceGroup().id)}'

@description('Specifies the name of the log analytics workspace.')
param containerAppLogAnalyticsName string = 'containerapp-log-${uniqueString(resourceGroup().id)}'

@description('Specifies the docker container image to deploy.')
param containerImage string = 'gcr.io/cloud-tagging-10302018/gtm-cloud-image:stable'

param memorySize string = '1' // The memory size of the container app

@description('Minimum number of replicas that will be deployed')
@minValue(0)
@maxValue(25)
param minReplica int = 1

@description('Maximum number of replicas that will be deployed')
@minValue(0)
@maxValue(25)
param maxReplica int = 3

@description('Number of CPU cores the container can use. Can be with a maximum of two decimals.')
@allowed([
  '0.25'
  '0.5'
  '0.75'
  '1'
  '1.25'
  '1.5'
  '1.75'
  '2'
])
param cpuCore string = '0.5'

@description('GTM Config String from your Server Container')
param GTMConfigString string


// variables
var appServicePlanName = toLower('AppServicePlan-${webAppName}')
var webSiteName = toLower('blazor-${webAppName}')


// -----------------------------------------------------
// ------------------ Resources -----------------------
// -----------------------------------------------------


// Create App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2020-06-01' = {
  name: appServicePlanName
  location: location
  properties: {
    reserved: true
  }
  sku: {
    name: sku
  }
  kind: 'windows'
}

// Create Web App
resource appService 'Microsoft.Web/sites@2020-06-01' = {
  name: webSiteName
  location: location
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      windowsFxVersion: windowsFxV
    }
  }
}

// Create repository connection for the web app if there is one (you can deploy from VSC / VS as well)
resource srcControls 'Microsoft.Web/sites/sourcecontrols@2021-01-01' = if (hasGitRepo) {
  parent: appService
  name: 'web'
  properties: {
    repoUrl: repositoryUrl
    branch: branch
    isManualIntegration: true
  }
}

// log analytics workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2021-06-01' = {
  name: containerAppLogAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
  }
}

// Create Azure Container Environment
resource containerAppEnv 'Microsoft.App/managedEnvironments@2022-01-01-preview' = {
  name: containerAppEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
  }
}


// Create Azure Container App for Preview
resource previewContainerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${containerAppName}-preview'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8080
        allowInsecure: true
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      revisionSuffix: 'firstrevision'
      containers: [
        {
          name: containerAppName
          image: containerImage
          env: [
            {
              name: 'CONTAINER_CONFIG'
              value: GTMConfigString
            }
            {
              name: 'RUN_AS_PREVIEW_SERVER'
              value: 'true'
            }
            {
              name: 'PORT'
              value: '8080'}
          ]
          resources: {
            cpu: json(cpuCore)
            memory: '${memorySize}Gi'
          }
        }
      ]
      scale: {
        minReplicas: minReplica
        maxReplicas: maxReplica
      }
  
    }
  }
}

// Create Azure Container App for server side tagging
resource serverContainerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${containerAppName}-server'
  location: location
  properties: {
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8081
        allowInsecure: true
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }
    }
    template: {
      revisionSuffix: 'firstrevision'
      containers: [
        {
          name: containerAppName
          image: containerImage
          env: [
            {
              name: 'CONTAINER_CONFIG'
              value: GTMConfigString
            }
            {
              name: 'SERVER_PREVIEW_URL'
              value: previewContainerApp.properties.configuration.ingress.fqdn
            }
            {
              name: 'PORT'
              value: '8081'}
          ]
          resources: {
            cpu: json(cpuCore)
            memory: '${memorySize}Gi'
          }
        }
      ]
      scale: {
        minReplicas: minReplica
        maxReplicas: maxReplica
      }
  
    }
  }
}


output previewContainerAppFQDN string = previewContainerApp.properties.configuration.ingress.fqdn
output serverContainerAppFQDN string = serverContainerApp.properties.configuration.ingress.fqdn
output webAppFQDN string = appService.properties.defaultHostName
