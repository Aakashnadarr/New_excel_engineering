variable "region" {
  description = "The AWS region to deploy the resources"
  type        = string
  default     = "ap-south-1" # Mumbai region where your ECR is
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
  default     = "new-excel-cluster"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "ecr_image_url" {
  description = "The full URL of your ECR image"
  type        = string
  default     = "575894693774.dkr.ecr.ap-south-1.amazonaws.com/new_excel_engineering:latest"
}

variable "container_port" {
  description = "The port your Docker container listens on"
  type        = number
  default     = 80
}