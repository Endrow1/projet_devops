variable "aws_region" {
  type    = string
  default = "eu-west-3" 
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "db_password" {
  type        = string
  sensitive   = true
}

variable "db_name" {
  type        = string
  default     = "projet_devops_db"
}

variable "db_user" {
  type        = string
  default     = "gotaga"
}

variable "ssh_public_key_path" {
  type        = string
}

variable "ssh_private_key_path" {
  type        = string
}

variable "aws_secret_access_key" {
  type        = string
}

variable "aws_access_key_id" {
  type        = string
}