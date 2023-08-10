# mig-blue-green
Code example used in [Zero-Downtime Blue/Green VM Deployments with Managed Instance Groups, Cloud Build & Terraform](https://cloud.google.com/build/docs/deploying-builds/deploy-compute-engine) user guide. For instructions on running this code sample, see the user guide.


```
(bot2-py3.11) ➜  infrastructure git:(main) ./setup.sh

######################################################
#                                                    #
#  Zero-Downtime Blue/Green VM Deployments Using     #
#  Managed Instance Groups, Cloud Build & Terraform  #
#                                                    #
######################################################


STARTED setup.sh:

It's safe to re-run this script to recreate all resources.

> Checking GCP CLI tool is installed
> No explicit project id provided, trying to infer

You are about to:
  * modify project bluegreen8957398475/182743579912
  * enable various GCP APIs
  * make Cloud Build editor of your project
  * execute Cloud Builds and Terraform plans to create
  * 2 VMs, 3 load balancers, 3 public IP addresses
  * incur charges in your billing account as a result

Enter 'yes' if you want to proceed:
yes

......................................................

> Received user consent
> Enabling required APIs
> Adding Cloud Build to roles/editor
> Adding Cloud Build to roles/source.admin
> Configuring bootstrap job
> Waiting API enablement propagation
> Executing bootstrap job

All done. Now you can:
  * manually run 'apply' and 'destroy' triggers to manage deployment lifecycle
  * commit change to 'infra/main.tfvars' and see 'apply' pipeline trigger automatically

Few key links:
  * Dashboard: https://console.cloud.google.com/home/dashboard?project=bluegreen8957398475
  * Repo: https://source.cloud.google.com/bluegreen8957398475/copy-of-mig-blue-green
  * Cloud Build Triggers: https://console.cloud.google.com/cloud-build/triggers;region=global?project=bluegreen8957398475
  * Cloud Build History: https://console.cloud.google.com/cloud-build/builds?project=bluegreen8957398475

.............................

COMPLETED!
(bot2-py3.11) ➜  infrastructure git:(main)


```



```commandline
(bot2-py3.11) ➜  infrastructure git:(main) ✗ ./setup.sh

######################################################
#                                                    #
#  Zero-Downtime Blue/Green VM Deployments Using     #
#  Managed Instance Groups, Cloud Build & Terraform  #
#                                                    #
######################################################


STARTED setup.sh:

It's safe to re-run this script to recreate all resources.

> Checking GCP CLI tool is installed
> No explicit project id provided, trying to infer

You are about to:
  * modify project bluegreen8957398475/182743579912
  * enable various GCP APIs
  * make Cloud Build editor of your project
  * execute Cloud Builds and Terraform plans to create
  * 2 VMs, 3 load balancers, 3 public IP addresses
  * incur charges in your billing account as a result

Enter 'yes' if you want to proceed:
yes

......................................................

> Received user consent
> Enabling required APIs
> Adding Cloud Build to roles/editor
> Adding Cloud Build to roles/source.admin
> Configuring bootstrap job
> Waiting API enablement propagation
> Executing bootstrap job

All done. Now you can:
  * manually run 'apply' and 'destroy' triggers to manage deployment lifecycle
  * commit change to 'infra/main.tfvars' and see 'apply' pipeline trigger automatically

Few key links:
  * Dashboard: https://console.cloud.google.com/home/dashboard?project=bluegreen8957398475
  * Repo: https://source.cloud.google.com/bluegreen8957398475/copy-of-mig-blue-green-disco
  * Cloud Build Triggers: https://console.cloud.google.com/cloud-build/triggers;region=global?project=bluegreen8957398475
  * Cloud Build History: https://console.cloud.google.com/cloud-build/builds?project=bluegreen8957398475

.............................

COMPLETED!
(bot2-py3.11) ➜  infrastructure git:(main) ✗ echo date
date
(bot2-py3.11) ➜  infrastructure git:(main) ✗ date
Thu Aug 10 04:18:43 CDT 2023

```

describe deployment:

```commandline

Starting Step #1 - "describe-deployment"
Step #1 - "describe-deployment": Already have image (with digest): gcr.io/cloud-builders/gcloud
Step #1 - "describe-deployment": Deployment configuration:
Step #1 - "describe-deployment": /**
Step #1 - "describe-deployment":  * Copyright 2023 Google LLC
Step #1 - "describe-deployment":  *
Step #1 - "describe-deployment":  * Licensed under the Apache License, Version 2.0 (the "License");
Step #1 - "describe-deployment":  * you may not use this file except in compliance with the License.
Step #1 - "describe-deployment":  * You may obtain a copy of the License at
Step #1 - "describe-deployment":  *
Step #1 - "describe-deployment":  *      http://www.apache.org/licenses/LICENSE-2.0
Step #1 - "describe-deployment":  *
Step #1 - "describe-deployment":  * Unless required by applicable law or agreed to in writing, software
Step #1 - "describe-deployment":  * distributed under the License is distributed on an "AS IS" BASIS,
Step #1 - "describe-deployment":  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
Step #1 - "describe-deployment":  * See the License for the specific language governing permissions and
Step #1 - "describe-deployment":  * limitations under the License.
Step #1 - "describe-deployment":  */
Step #1 - "describe-deployment":
Step #1 - "describe-deployment": # [START cloudbuild_terraform_variables]
Step #1 - "describe-deployment": MIG_VER_BLUE     = "v1"
Step #1 - "describe-deployment": MIG_VER_GREEN    = "v1"
Step #1 - "describe-deployment": MIG_ACTIVE_COLOR = "blue"
Step #1 - "describe-deployment": # [END cloudbuild_terraform_variables]
Step #1 - "describe-deployment": Here is how to connect to:
Step #1 - "describe-deployment": 	* active color MIG: http://35.212.239.108/
Step #1 - "describe-deployment": 	* blue color MIG: http://35.212.204.224/
Step #1 - "describe-deployment": 	* green color MIG: http://35.212.181.22/
Step #1 - "describe-deployment": Good luck!
Finished Step #1 - "describe-deployment"
PUSH
DONE
Step #0 - "run-terraform-apply":
```

more

```commandline
All done. Now you can:
  * manually run 'apply' and 'destroy' triggers to manage deployment lifecycle
  * commit change to 'infra/main.tfvars' and see 'apply' pipeline trigger automatically

Few key links:
  * Dashboard: https://console.cloud.google.com/home/dashboard?project=bluegreen8957398475
  * Repo: https://source.cloud.google.com/bluegreen8957398475/copy-of-mig-blue-green-disco
  * Cloud Build Triggers: https://console.cloud.google.com/cloud-build/triggers;region=global?project=bluegreen8957398475
  * Cloud Build History: https://console.cloud.google.com/cloud-build/builds?project=bluegreen8957398475

.............................

COMPLETED!
(bot2-py3.11) ➜  infrastructure git:(main) ✗ date
Thu Aug 10 04:45:32 CDT 2023

```
