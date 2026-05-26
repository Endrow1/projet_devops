output "app_public_ips" {
  value = aws_instance.app[*].public_ip
}

output "db_private_ip" {
  value = aws_instance.db.private_ip
}

output "load_balancer_dns" {
  value = aws_lb.app_lb.dns_name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.backups.bucket
}