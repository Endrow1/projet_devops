# =========================
# VMs applicatives
# =========================

resource "aws_instance" "app" {
  count = 2

  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  subnet_id = aws_subnet.public.id

  vpc_security_group_ids = [
    aws_security_group.app_sg.id
  ]

  tags = {
    Name = "${var.project_name}-app-${count.index + 1}"
    Role = "application"
  }
}

# =========================
# VM Base de données
# =========================

resource "aws_instance" "db" {
  ami           = var.ami_id
  instance_type = var.instance_type
  key_name      = var.key_name

  subnet_id = aws_subnet.private.id

  vpc_security_group_ids = [
    aws_security_group.db_sg.id
  ]

  tags = {
    Name = "${var.project_name}-db"
    Role = "database"
  }
}