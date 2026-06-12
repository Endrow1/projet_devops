output "load_balancer_dns" {
  value= aws_lb.app_alb.dns_name
}