resource "aws_lb" "app_lb" {
  name               = "${var.project_name}-lb"
  internal           = false
  load_balancer_type = "application"

  security_groups = [
    aws_security_group.lb_sg.id
  ]

  subnets = [
    aws_subnet.public.id,
    aws_subnet.public_b.id
  ]

  tags = {
    Name = "${var.project_name}-lb"
  }
}

resource "aws_lb_target_group" "app_tg" {
  name     = "${var.project_name}-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path = "/"
    port = "5000"
  }
}

resource "aws_lb_target_group_attachment" "app_attach" {
  count = 2

  target_group_arn = aws_lb_target_group.app_tg.arn
  target_id        = aws_instance.app[count.index].id
  port             = 5000
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app_tg.arn
  }
}