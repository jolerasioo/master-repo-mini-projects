# Containerizing Google Tag Manager with Azure Container Apps

This repository contains the instructions and files to set up Google Tag Manager for Google Analytics on Azure Container Apps. It leverages a sample Blazor .NET app and contains the necessary Bicep IaC to run it.

(insert arhcitecture and links)

## Requirements
0. Azure Subscription
1. One web application with some HTML code (you can use this repository)
2. Google Tag Manager profile (can be set up for free)
3. Google Analytics profile (can be set up for free)

## Steps
### Step 1: Deploy your web application
This repository contains a sample Blazor web app that you can deploy into App Service via the extension on VSC or CI/CD.

0. Create the App Service instance for .NET 6 (IaC template to be added)
1. Deploy the web app: for simplicity use the VSC Azure Extension or VS Publish features

### Step 2: Create a GTM server container
0. Open your GTM profile and create a new **server** container (Admin > "+" on the container tab), with a recognizeable name, and push create
1. On the pop-up, select Manual Deployment and copy the configuration string

### Step 3: Deploy and configure the Preview Tagging container app

Follow this [link](https://developers.google.com/tag-platform/tag-manager/server-side/manual-setup-guide) with the Google Tag Manager documentation for Steps 3 and 4.

0. Deploy one container app for preview tagging, with ingress configufured (for demo purposes, select accept traffic from anywhere)
1. Add the environment variables from the link, which you can configure as a secret if you want to or keep them as manual:
    - `CONTAINER_CONFIG` = `<your container config string>`
    - `RUN_AS_PREVIEW_SERVER` = `true`
    - (optional) `PORT` = `<same port as ingress>`

### Step 4: Deploy and configure the Server Side Tagging container app

Follow this [link](https://developers.google.com/tag-platform/tag-manager/server-side/manual-setup-guide) with the Google Tag Manager documentation for Steps 3 and 4.

Repeate the steps from step 3, but changing the second environment variable to SERVER_PREVIEW_URL = ingress url from preview ACApp.

### Step 5: Validate the deployments
Run `<ingress url>/healthz` for each container app, and you will recieve a 200 OK response if everything is correct. Refer to the Google Tag Manager documentation for troubleshooting.

### Step 6: Configure GTag on GTM and your app

[GTM documentation](https://developers.google.com/tag-platform/tag-manager/server-side/intro#configure_gtagjs)

You can find the `TAG_ID` on Google Analytics, which you'll have to create. Navigate to Admin > Data collection and modification > data streams. It will appear Measurement ID. Remeber to change it on the two places that it appears!

### Step 4: Run the app and validate
Open the web app and press F12 to view the developer settings. Go to Network to view the logs. Move around the app/ refresh. Look for the *collect* log and check that it's pointing at ther server side container app and that it's a 200 OK response.

Navigate on Google Analytics to the Real Time report and check that it's catching your data correctly. It might take a few mins to warm up depending on the configuration for the apps.
