/**
 * Copyright 2023 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

variable "project" {
  type = string
}

variable "app_version" {
  type = string
}

variable "ns" {
  type = string
}

variable "color" {
  type = string
}

variable "google_compute_network" {
  type = any
}

variable "google_compute_subnetwork" {
  type = any
}

variable "google_compute_subnetwork_proxy_only" {
  type = any
}

locals {
  fw-allow-health-check          = "${var.ns}${var.color}-fw-allow-health-check"
  l7-xlb-basic-check             = "${var.ns}${var.color}-l7-xlb-basic-check"
  l7-xlb-backend-service         = "${var.ns}${var.color}-l7-xlb-backend-service"
  regional-l7-xlb-map            = "${var.ns}${var.color}-regional-l7-xlb-map"
  l7-xlb-proxy                   = "${var.ns}${var.color}-l7-xlb-proxy"
  l7-xlb-forwarding-rule-colored = "${var.ns}${var.color}-l7-xlb-forwarding-rule-colored"
  l7-xlb-backend-template        = "${var.ns}${var.color}-l7-xlb-backend-template-${var.app_version}"
  l7-xlb-group-manager           = "${var.ns}${var.color}-l7-xlb-group-manager-${var.app_version}"
  base_instance_name             = "${var.ns}${var.color}-vm"
  firewall-name                  = "${var.ns}${var.color}-firewall"
}

# [START cloudbuild_create_before_destroy]
resource "google_compute_instance_template" "default" {
  name = local.l7-xlb-backend-template
  disk {
    auto_delete  = true
    boot         = true
    device_name  = "persistent-disk-0"
    mode         = "READ_WRITE"
    source_image = "projects/debian-cloud/global/images/family/debian-10"
    type         = "PERSISTENT"
  }
  labels = {
    managed-by-cnrm = "true"
  }
  machine_type = "e2-micro"
  metadata = {
    enable-oslogin = "false"
    startup-script = <<EOF
    #! /bin/bash
    sudo apt-get update
    # required
    sudo apt-get install -y build-essential zlib1g-dev libssl-dev
    sudo apt-get install -y libreadline-dev libbz2-dev libsqlite3-dev libffi-dev
    curl -sS https://webi.sh/pyenv | sh
    pyenv install -v 3.10.7
    pyenv global 3.10.7
    curl -sSL https://install.python-poetry.org | python3 -
    git clone https://github.com/ekand/bot2.git
    cd bot2
    gcloud secrets versions access 1 --secret=dot-env > .env
    export BOT2_WORKING_DIR=$(pwd)
    export BOT2_PYTHON_FILE_NAME=main.py
    poetry shell
    poetry install
    export POETRY_ENV_EXECUTABLE = $(which python)
    vm_hostname="$(curl -H "Metadata-Flavor:Google" \
    http://169.254.169.254/computeMetadata/v1/instance/name)"
    sudo echo "[Unit]
Description=Discord Bot2
After=multi-user.target
[Service]
Type=simple
Restart=always
ExecStart="$(poetry shell && which python) /home/bot2/main.py"
[Install]
WantedBy=multi-user.target" > /etc/systemd/system/discord-bot2.service
    sudo systemctl restart discord-bot2
    EOF
  }
  network_interface {
    access_config {
      network_tier = "PREMIUM"
    }
    network    = var.google_compute_network.id
    subnetwork = var.google_compute_subnetwork.id
  }
  region = "us-west1"
  scheduling {
    automatic_restart   = true
    on_host_maintenance = "MIGRATE"
    provisioning_model  = "STANDARD"
  }
  tags = ["load-balanced-backend", "allow-iap-ssh"]

  # NOTE: the name of this resource must be unique for every update;
  #       this is wy we have a app_version in the name; this way
  #       new resource has a different name vs old one and both can
  #       exists at the same time
  lifecycle {
    create_before_destroy = true
  }
}
# [END cloudbuild_create_before_destroy]

resource "google_compute_instance_group_manager" "default" {
  name = local.l7-xlb-group-manager
  zone = "us-west1-a"
  named_port {
    name = "http"
    port = 80
  }
  version {
    instance_template = google_compute_instance_template.default.id
    name              = "primary"
  }
  base_instance_name = local.base_instance_name
  target_size        = 1

  # NOTE: the name of this resource must be unique for every update;
  #       this is wy we have a app_version in the name; this way
  #       new resource has a different name vs old one and both can
  #       exists at the same time
  lifecycle {
    create_before_destroy = true
  }
}

resource "google_compute_address" "active" {
  name         = "${var.ns}${var.color}-address-name"
  address_type = "EXTERNAL"
  network_tier = "STANDARD"
  region       = "us-west1"
}

resource "google_compute_region_health_check" "default" {
  name               = local.l7-xlb-basic-check
  check_interval_sec = 5
  healthy_threshold  = 2
  http_health_check {
    port_specification = "USE_SERVING_PORT"
    proxy_header       = "NONE"
    request_path       = "/"
  }
  region              = "us-west1"
  timeout_sec         = 5
  unhealthy_threshold = 2
}

resource "google_compute_region_backend_service" "default" {
  name                  = local.l7-xlb-backend-service
  region                = "us-west1"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  health_checks         = [google_compute_region_health_check.default.id]
  protocol              = "HTTP"
  session_affinity      = "NONE"
  timeout_sec           = 30
  backend {
    group           = google_compute_instance_group_manager.default.instance_group
    balancing_mode  = "UTILIZATION"
    capacity_scaler = 1
  }
}

resource "google_compute_region_url_map" "default" {
  name            = local.regional-l7-xlb-map
  region          = "us-west1"
  default_service = google_compute_region_backend_service.default.id
}

resource "google_compute_region_target_http_proxy" "default" {
  name    = local.l7-xlb-proxy
  region  = "us-west1"
  url_map = google_compute_region_url_map.default.id
}

resource "google_compute_forwarding_rule" "colored" {
  project               = var.project
  name                  = local.l7-xlb-forwarding-rule-colored
  provider              = google-beta
  depends_on            = [var.google_compute_subnetwork_proxy_only]
  region                = "us-west1"
  ip_protocol           = "TCP"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  port_range            = "80"
  target                = google_compute_region_target_http_proxy.default.id
  network               = var.google_compute_network.id
  ip_address            = google_compute_address.active.id
  network_tier          = "STANDARD"
}

resource "google_compute_firewall" "allow_iap_ssh" {
  name    = local.firewall-name
  network = var.google_compute_network.id  # Change to the appropriate network name if needed

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["35.235.240.0/20"]
  target_tags  = ["allow-iap-ssh"]
}

output "google_compute_instance_group_manager_default" {
  value = google_compute_instance_group_manager.default
}
