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
