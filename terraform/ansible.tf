resource "local_file" "ansible_inventory" {
  filename = "../ansible/inventory.ini"

  content = <<EOT
[app_servers]
${aws_instance.app_server[0].public_ip} ansible_user=ubuntu
${aws_instance.app_server[1].public_ip} ansible_user=ubuntu

[db_server]
${aws_db_instance.mysql.address}

[all:vars]
db_host=${aws_db_instance.mysql.address}
aws_s3_bucket=${aws_s3_bucket.backups.id}
db_user=${var.db_user}
db_name=${var.db_name}
db_password=${var.db_password}
aws_access_key=${var.aws_access_key_id}
aws_secret_key=${var.aws_secret_access_key}
ansible_ssh_private_key_file=${var.ssh_private_key_path}
ansible_ssh_common_args='-o StrictHostKeyChecking=no'
EOT
}