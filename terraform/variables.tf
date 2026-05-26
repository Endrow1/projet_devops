variable "aws_region" {
  description = "Région AWS"
  type        = string
}

variable "project_name" {
  description = "Nom du projet"
  type        = string
}

variable "ami_id" {
  description = "AMI Ubuntu"
  type        = string
}

variable "instance_type" {
  description = "Type des instances"
  type        = string
  default     = "t2.micro"
}

variable "key_name" {
  description = "Nom de la clé SSH AWS"
  type        = string
}

variable "my_ip" {
  description = "IP autorisée en SSH"
  type        = string
}